import re
import os
import email
import pickle
import string
from urllib.parse import urlparse

import nltk
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

# --- ADDED ---: เพิ่ม import สำหรับ Hugging Face Datasets
from datasets import load_dataset

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from scipy.sparse import hstack

# Download NLTK data if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class PhishingDetector:
    def __init__(self):
        self.suspicious_keywords = [
            'urgent', 'verify', 'click here', 'limited time', 'act now',
            'congratulations', 'winner', 'prize', 'free', 'offer',
            'suspended', 'expired', 'confirm', 'update', 'security alert',
            'password', 'credit card', 'bank account', 'ssn',
            'ด่วน', 'ยืนยัน', 'คลิกที่นี่', 'ฟรี', 'รางวัล', 'หมดเวลา',
            'อัปเดต', 'แจ้งเตือน', 'ระงับ', 'ยกเลิก', 'รหัสผ่าน', 'บัตรเครดิต'
        ]
        self.suspicious_domains = [
            'bit.ly', 'tinyurl.com', 't.co', 'goo.gl',
            'shortened.link', 'short.link'
        ]

        self.vectorizer = TfidfVectorizer(
            max_features=2500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.model = LogisticRegression(
            solver='liblinear',
            random_state=42,
            class_weight='balanced',
            C=5
        )
        self.is_trained = False

    def _clean_text(self, text):
        if not isinstance(text, str):
            return ""
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text()
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    # --- [NEW] --- ฟังก์ชันสำหรับตรวจสอบ URL อย่างปลอดภัย
    def _safe_url_parse(self, url):
        """
        ฟังก์ชัน urlparse ที่ดักจับ ValueError เพื่อป้องกันโปรแกรมล่ม
        """
        try:
            # คืนค่า network location (domain) ของ URL
            return urlparse(url).netloc
        except ValueError:
            # หากเจอ URL ที่มีปัญหา (เช่น Invalid IPv6) ให้คืนค่าเป็น string ว่าง
            # เพื่อให้การตรวจสอบ 'in' ทำงานต่อไปได้โดยไม่เกิด error
            return ""

    # --- [MODIFIED] --- ปรับปรุงการสกัด Feature ให้ซับซ้อนขึ้น
    def extract_features(self, content):
        if not isinstance(content, str):
            content = ""

        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)

        url_count = len(urls)
        has_ip_url = 1 if any(re.match(r"http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url) for url in urls) else 0

        # --- [FIXED] --- แก้ไขจุดที่เกิด Error โดยเรียกใช้ _safe_url_parse
        # แทนที่จะเรียกใช้ urlparse(url).netloc โดยตรง
        has_shortened_url = 1 if any(any(sus_domain in self._safe_url_parse(url) for sus_domain in self.suspicious_domains) for url in urls) else 0

        has_at_in_url = 1 if any('@' in url for url in urls) else 0
        suspicious_keyword_count = sum(1 for keyword in self.suspicious_keywords if keyword in content.lower())
        html_tag_count = len(re.findall(r"<[^>]+>", content))
        digit_count = sum(c.isdigit() for c in content)
        content_len = len(content) if len(content) > 0 else 1
        uppercase_ratio = sum(1 for c in content if c.isupper()) / content_len

        features = np.array([
            url_count,
            has_ip_url,
            has_shortened_url,
            has_at_in_url,
            suspicious_keyword_count,
            html_tag_count,
            digit_count,
            uppercase_ratio
        ])
        return features

    def train_with_combined_data(self, local_csv_path=None, test_size=0.2, save_model=True):
        print("===== เริ่มกระบวนการเทรนโมเดล (ฉบับปรับปรุง) =====")

        # --- 1. โหลดข้อมูลจากไฟล์ CSV ---
        print("\n[ขั้นตอนที่ 1/4] กำลังโหลดและเตรียมข้อมูลจากไฟล์ CSV...")
        df_local = pd.DataFrame()
        if local_csv_path is None:
            # ปรับ path ให้ยืดหยุ่นมากขึ้น
            local_csv_path = self.find_dataset_file("Phishing_Email.csv")

        if local_csv_path:
            loaded_df = self.load_dataset(local_csv_path)
            if loaded_df is not None and 'Email Text' in loaded_df and 'Email Type' in loaded_df:
                df_local = loaded_df[['Email Text', 'Email Type']].rename(columns={'Email Text': 'email', 'Email Type': 'label'})
                print(f"เตรียมข้อมูลจาก CSV สำเร็จ: {len(df_local)} รายการ")
            else:
                print("ไฟล์ CSV ไม่พบคอลัมน์ที่คาดหวัง ('Email Text', 'Email Type')")
        else:
            print("ไม่พบไฟล์ 'Phishing_Email.csv'")

        # --- 2. โหลดข้อมูลจาก Hugging Face ---
        print("\n[ขั้นตอนที่ 2/4] กำลังดาวน์โหลดและเตรียมข้อมูลจาก Hugging Face...")
        df_hf = pd.DataFrame()
        try:
            hf_dataset = load_dataset("kmack/Phishing_urls", split='train')
            df_hf_all = hf_dataset.to_pandas()
            if 'text' in df_hf_all and 'label' in df_hf_all:
                df_hf = df_hf_all[['text', 'label']].rename(columns={'text': 'email'})
                print(f"เตรียมข้อมูลจาก Hugging Face สำเร็จ: {len(df_hf)} รายการ")
            else:
                print("Dataset จาก Hugging Face ไม่พบคอลัมน์ที่คาดหวัง ('text', 'label')")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการดาวน์โหลดข้อมูลจาก Hugging Face: {e}")

        # --- 3. รวมข้อมูล ---
        print("\n[ขั้นตอนที่ 3/4] กำลังรวมข้อมูลที่จัดรูปแบบแล้ว...")
        if not df_local.empty or not df_hf.empty:
            combined_df = pd.concat([df_local, df_hf], ignore_index=True)
        else:
            print("ไม่สามารถโหลดข้อมูลจากแหล่งใดได้เลย สิ้นสุดการเทรน")
            return False

        # --- 4. เตรียมข้อมูลและเทรนโมเดล ---
        print("\n[ขั้นตอนที่ 4/4] กำลังเตรียมข้อมูล, สร้าง Feature และเทรนโมเดล...")
        texts, labels = self.preprocess_data(combined_df)
        if texts is None or labels is None:
            return False

        engineered_features = np.array([self.extract_features(text) for text in texts])
        cleaned_texts = [self._clean_text(text) for text in texts]

        X_train_text, X_test_text, \
        X_train_features, X_test_features, \
        y_train, y_test = train_test_split(
            cleaned_texts, engineered_features, labels,
            test_size=test_size, random_state=42, stratify=labels
        )
        print(f"ข้อมูลการเทรน: {len(X_train_text)} รายการ, ข้อมูลการทดสอบ: {len(X_test_text)} รายการ")

        X_train_tfidf = self.vectorizer.fit_transform(X_train_text)
        X_test_tfidf = self.vectorizer.transform(X_test_text)

        X_train_combined = hstack([X_train_tfidf, X_train_features])
        X_test_combined = hstack([X_test_tfidf, X_test_features])

        print("กำลังเทรนโมเดล Logistic Regression...")
        self.model.fit(X_train_combined, y_train)

        y_pred = self.model.predict(X_test_combined)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\nผลการเทรน:\nAccuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))

        self.is_trained = True
        if save_model:
            self.save_model()
        return True

    def analyze_email(self, content):
        if not self.is_trained:
            return {'risk_score': 0.0, 'features': {}, 'recommendations': ['โมเดลยังไม่พร้อมใช้งาน']}
        try:
            engineered_features = self.extract_features(content)
            cleaned_content = self._clean_text(content)
            tfidf_features = self.vectorizer.transform([cleaned_content])
            combined_features = hstack([tfidf_features, engineered_features.reshape(1, -1)])
            risk_score = self.model.predict_proba(combined_features)[0][1]

            feature_names = [
                'url_count', 'has_ip_url', 'has_shortened_url', 'has_at_in_url',
                'suspicious_keyword_count', 'html_tag_count', 'digit_count', 'uppercase_ratio'
            ]
            readable_features = dict(zip(feature_names, engineered_features))
            recommendations = self.generate_recommendations(risk_score, readable_features)

            return {
                'risk_score': float(risk_score),
                'features': readable_features,
                'recommendations': recommendations
            }
        except Exception as e:
            print(f"เกิดข้อผิดพลาดระหว่างวิเคราะห์: {e}")
            return {'risk_score': 0.0, 'features': {}, 'recommendations': [f'เกิดข้อผิดพลาด: {e}']}

    # ฟังก์ชันอื่นๆ ที่เหลือ (load_dataset, preprocess_data, find_dataset_file, etc.)
    # ... สามารถคัดลอกส่วนที่เหลือของคลาสมาวางต่อจากตรงนี้ได้เลย ...
    def load_dataset(self, file_path):
        try:
            actual_path = None
            possible_paths = [
                file_path,
                os.path.join(os.getcwd(), file_path),
                os.path.join(os.getcwd(), 'data', file_path) # เพิ่มการค้นหาใน subfolder 'data'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    actual_path = path
                    break
            if actual_path is None:
                raise FileNotFoundError(f"ไม่พบไฟล์ {file_path}")

            print(f"พบไฟล์ที่: {actual_path}")
            file_extension = os.path.splitext(actual_path)[1].lower()

            if file_extension == '.csv':
                encodings = ['utf-8', 'utf-8-sig', 'cp874', 'iso-8859-1', 'windows-1252']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(actual_path, encoding=encoding)
                        print(f"ใช้ encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                if df is None:
                    raise ValueError("ไม่สามารถอ่านไฟล์ CSV ได้")
                return df
            else:
                raise ValueError(f"ไม่รองรับไฟล์นามสกุล {file_extension}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
            return None

    def preprocess_data(self, df):
        try:
            df.dropna(subset=['email', 'label'], inplace=True)
            if df['label'].dtype == 'object':
                label_map = {
                    'Phishing Email': 1, 'Safe Email': 0, 'phishing': 1,
                    'Phishing': 1, 'PHISHING': 1, 'safe': 0, 'Safe': 0,
                    'SAFE': 0, 'legitimate': 0, 'Legitimate': 0, 'LEGITIMATE': 0,
                }
                df['label'] = df['label'].map(label_map)
            df['label'] = pd.to_numeric(df['label'], errors='coerce')
            df.dropna(subset=['label'], inplace=True)
            df['label'] = df['label'].astype(int)
            return df['email'].astype(str).tolist(), df['label'].tolist()
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเตรียมข้อมูล: {str(e)}")
            return None, None

    def find_dataset_file(self, filename="Phishing_Email.csv"):
        # ค้นหาในตำแหน่งปัจจุบันและในโฟลเดอร์ 'data'
        search_paths = [filename, os.path.join('data', filename)]
        for path in search_paths:
            if os.path.exists(path):
                return path
        return None

    def save_model(self, model_path='phishing_model_v2.pkl', vectorizer_path='tfidf_vectorizer_v2.pkl'):
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            print(f"บันทึกโมเดลสำเร็จที่: {model_path} และ {vectorizer_path}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการบันทึกโมเดล: {str(e)}")

    def load_model(self, model_path='phishing_model_v2.pkl', vectorizer_path='tfidf_vectorizer_v2.pkl'):
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            self.is_trained = True
            print(f"โหลดโมเดลสำเร็จจาก: {model_path}")
            return True
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดโมเดล: {str(e)}")
            return False

    def generate_recommendations(self, score, features):
        recommendations = []
        if score >= 0.8:
            recommendations.extend(['ความเสี่ยงสูงมาก', 'ไม่ควรคลิกลิงก์หรือให้ข้อมูลส่วนตัว', 'แนะนำให้ลบอีเมลนี้ทิ้งทันที'])
        elif score >= 0.5:
            recommendations.extend(['ความเสี่ยงสูง', 'ควรตรวจสอบผู้ส่งและลิงก์อย่างระมัดระวังที่สุด', 'หลีกเลี่ยงการดาวน์โหลดไฟล์แนบ'])
        elif score >= 0.2:
            recommendations.extend(['ความเสี่ยงปานกลาง', 'โปรดใช้ความระมัดระวังในการโต้ตอบ'])
        else:
            recommendations.extend(['ความเสี่ยงต่ำ', 'ดูเหมือนจะปลอดภัย แต่ควรตรวจสอบผู้ส่งเสมอ'])

        if features.get('has_shortened_url', 0) > 0:
            recommendations.append('พบ URL ย่อส่วน โปรดระวังก่อนคลิก')
        if features.get('suspicious_keyword_count', 0) > 5:
            recommendations.append('มีคำที่สร้างความเร่งด่วนหรือน่าสงสัยจำนวนมาก')
        return recommendations

# ส่วนที่ใช้ในการรันและทดสอบ (เหมือนเดิม แต่เรียกใช้ PhishingDetector ที่อัปเกรดแล้ว)
phishing_detector = PhishingDetector()

# ... (คัดลอก initialize_model, train_model_from_dataset, test_model จากโค้ดเดิม) ...
def initialize_model():
    print("Initializing Phishing Detector Model (v2)...")
    if phishing_detector.load_model():
        print("Model loaded successfully from saved files.")
        return True
    print("\nCould not find saved model. Starting training process...")
    if phishing_detector.train_with_combined_data():
        print("\nNew model trained and saved successfully!")
    else:
        print("\nFailed to train the model.")
    return True

def train_model_from_dataset(force_retrain=False):
    global phishing_detector
    if phishing_detector.is_trained and not force_retrain:
        print("โมเดลถูกเทรนแล้ว หากต้องการเทรนใหม่ให้ใช้ force_retrain=True")
        return True
    print("Forcing model retraining...")
    phishing_detector.train_with_combined_data()

def test_model():
    if not phishing_detector.is_trained:
        print("\nไม่สามารถทดสอบโมเดลได้ เนื่องจากยังไม่ได้เทรน")
        return
    print("\n" + "="*50)
    print("Testing IMPROVED model with sample data...")
    test_cases = [
        'URGENT! Your bank account has been compromised. Please CLICK HERE http://123.45.67.89/login to verify your password immediately.',
        'Hi team, please see the attached document for the Q3 financial report. Let me know if you have questions.',
        'Congratulations! you won a $1000 gift card from amazon, claim now http://bit.ly/totally-not-a-scam before it expires!',
        '<html><body><p><b>Update</b> your account information for Microsoft by clicking <a href="http://secure-login-microsoft.com.malicious.net/auth">here</a></p></body></html>'
    ]
    for text in test_cases:
        result = phishing_detector.analyze_email(text)
        print(f"\nText: {text[:70]}...")
        print(f"Risk Score: {result['risk_score']:.4f}")
        print(f"Detected Features: {result['features']}")
        print(f"Recommendations: {', '.join(result['recommendations'])}")
    print("="*50)

if __name__ == "__main__":
    print("Running phishing_detector_v2.py as a standalone script.")
    # เทรนโมเดล (ถ้ายังไม่มีไฟล์ .pkl มันจะถูกสร้างขึ้น)
    initialize_model()
    # ทดสอบโมเดล
    test_model()