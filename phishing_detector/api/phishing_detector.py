import re
import os
import email
import pickle
import string
from urllib.parse import urlparse

import nltk
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup  # --- [NEW] --- สำหรับลบ HTML tags

# --- ADDED ---: เพิ่ม import สำหรับ Hugging Face Datasets
from datasets import load_dataset

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression  # --- [MODIFIED] --- เปลี่ยนโมเดล
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from scipy.sparse import hstack  # --- [NEW] --- สำหรับรวม sparse matrix กับ dense array

# Download NLTK data if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class PhishingDetector:
    def __init__(self):
        # --- [MODIFIED] --- ปรับปรุง Keywords และเพิ่มตัวแปรสำหรับ Feature ใหม่ๆ
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

        # --- [MODIFIED] --- ปรับ Vectorizer และเปลี่ยน Model
        self.vectorizer = TfidfVectorizer(
            max_features=2500,  # เพิ่มจำนวน features
            stop_words='english',
            ngram_range=(1, 2)  # พิจารณาคำติดกัน 2 คำด้วย
        )
        self.model = LogisticRegression(
            solver='liblinear',
            random_state=42,
            class_weight='balanced',  # ช่วยจัดการข้อมูลที่ไม่สมดุล
            C=5 # Regularization parameter
        )
        self.is_trained = False

    # --- [NEW] --- ฟังก์ชันทำความสะอาดข้อความ
    def _clean_text(self, text):
        """
        ทำความสะอาดข้อความ: ลบ HTML, punctuation, และทำให้เป็นตัวพิมพ์เล็ก
        """
        if not isinstance(text, str):
            return ""
        # 1. ใช้ BeautifulSoup เพื่อดึงข้อความจาก HTML
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text()
        # 2. ทำให้เป็นตัวพิมพ์เล็ก
        text = text.lower()
        # 3. ลบ Punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    # --- [MODIFIED] --- ปรับปรุงการสกัด Feature ให้ซับซ้อนขึ้น
    def extract_features(self, content):
        """
        สกัด Feature ที่สร้างขึ้นเอง (Engineered Features) จากเนื้อหาอีเมล
        จะ return เป็น numpy array ของตัวเลข
        """
        if not isinstance(content, str):
            content = ""

        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # Feature 1: จำนวน URL ทั้งหมด
        url_count = len(urls)
        
        # Feature 2: มี IP Address ใน URL หรือไม่ (1=มี, 0=ไม่มี)
        has_ip_url = 1 if any(re.match(r"http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url) for url in urls) else 0

        # Feature 3: มี URL ย่อส่วนหรือไม่
        has_shortened_url = 1 if any(any(sus_domain in urlparse(url).netloc for sus_domain in self.suspicious_domains) for url in urls) else 0
        
        # Feature 4: มีสัญลักษณ์ '@' ใน URL หรือไม่ (เทคนิคหลอกลวง)
        has_at_in_url = 1 if any('@' in url for url in urls) else 0
        
        # Feature 5: จำนวนคำต้องสงสัยที่พบ
        suspicious_keyword_count = sum(1 for keyword in self.suspicious_keywords if keyword in content.lower())
        
        # Feature 6: จำนวน HTML tags (บ่งบอกความซับซ้อนที่อาจไม่จำเป็น)
        html_tag_count = len(re.findall(r"<[^>]+>", content))
        
        # Feature 7: จำนวนตัวเลขทั้งหมด
        digit_count = sum(c.isdigit() for c in content)

        # Feature 8: สัดส่วนตัวอักษรพิมพ์ใหญ่ (ตะโกน)
        content_len = len(content) if len(content) > 0 else 1
        uppercase_ratio = sum(1 for c in content if c.isupper()) / content_len

        # คืนค่าเป็น list หรือ array ที่มีลำดับแน่นอน
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

    # --- [MODIFIED] --- กระบวนการเทรนใหม่ทั้งหมด
    def train_with_combined_data(self, local_csv_path=None, test_size=0.2, save_model=True):
        print("===== เริ่มกระบวนการเทรนโมเดล (ฉบับปรับปรุง) =====")

        # ส่วนของการโหลดข้อมูล (ขั้นตอน 1-3) เหมือนเดิม...
        # ... (คัดลอกส่วนโหลดข้อมูลจากโค้ดเดิมมาวางตรงนี้) ...
        # --- 1. โหลดและเตรียมข้อมูลจากไฟล์ CSV เดิม ---
        print("\n[ขั้นตอนที่ 1/4] กำลังโหลดและเตรียมข้อมูลจากไฟล์ CSV...")
        df_local = pd.DataFrame()
        if local_csv_path is None:
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

        # --- 2. โหลดและเตรียมข้อมูลจาก Hugging Face ---
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

        # --- 3. รวมข้อมูลที่เตรียมแล้ว ---
        print("\n[ขั้นตอนที่ 3/4] กำลังรวมข้อมูลที่จัดรูปแบบแล้ว...")
        if not df_local.empty or not df_hf.empty:
            combined_df = pd.concat([df_local, df_hf], ignore_index=True)
        else:
            print("ไม่สามารถโหลดข้อมูลจากแหล่งใดได้เลย สิ้นสุดการเทรน")
            return False

        # --- 4. เตรียมข้อมูล, สร้าง Feature และเทรนโมเดล ---
        print("\n[ขั้นตอนที่ 4/4] กำลังเตรียมข้อมูล, สร้าง Feature และเทรนโมเดล...")
        
        # 4.1. Preprocess ข้อมูลพื้นฐาน
        texts, labels = self.preprocess_data(combined_df)
        if texts is None or labels is None:
            return False

        # 4.2. สร้าง Engineered Features จาก 'texts' ดิบ (ก่อน clean)
        engineered_features = np.array([self.extract_features(text) for text in texts])

        # 4.3. ทำความสะอาดข้อความสำหรับ TF-IDF
        cleaned_texts = [self._clean_text(text) for text in texts]
        
        # 4.4. แบ่งข้อมูลทั้งหมด (ทั้ง cleaned_texts, engineered_features, และ labels)
        X_train_text, X_test_text, \
        X_train_features, X_test_features, \
        y_train, y_test = train_test_split(
            cleaned_texts, engineered_features, labels,
            test_size=test_size, random_state=42, stratify=labels
        )
        print(f"ข้อมูลการเทรน: {len(X_train_text)} รายการ, ข้อมูลการทดสอบ: {len(X_test_text)} รายการ")
        
        # 4.5. ทำ TF-IDF Vectorization
        X_train_tfidf = self.vectorizer.fit_transform(X_train_text)
        X_test_tfidf = self.vectorizer.transform(X_test_text)

        # 4.6. *** จุดสำคัญ: รวม TF-IDF features กับ Engineered features ***
        X_train_combined = hstack([X_train_tfidf, X_train_features])
        X_test_combined = hstack([X_test_tfidf, X_test_features])
        
        # 4.7. เทรนโมเดลด้วยข้อมูลที่รวมแล้ว
        print("กำลังเทรนโมเดล Logistic Regression...")
        self.model.fit(X_train_combined, y_train)

        # 4.8. ประเมินผล
        y_pred = self.model.predict(X_test_combined)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nผลการเทรน:\nAccuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))
        
        self.is_trained = True
        if save_model:
            self.save_model()
        return True

    # --- [MODIFIED] --- กระบวนการวิเคราะห์ใหม่ทั้งหมด
    def analyze_email(self, content):
        if not self.is_trained:
            print("โมเดลยังไม่ได้เทรน ไม่สามารถวิเคราะห์ได้")
            return {'risk_score': 0.0, 'features': {}, 'recommendations': ['โมเดลยังไม่พร้อมใช้งาน']}

        try:
            # 1. สกัด Engineered Features จาก content ดิบ
            engineered_features = self.extract_features(content)
            
            # 2. ทำความสะอาด content สำหรับ TF-IDF
            cleaned_content = self._clean_text(content)
            
            # 3. แปลงเป็น TF-IDF vector
            tfidf_features = self.vectorizer.transform([cleaned_content])
            
            # 4. *** จุดสำคัญ: รวม features ทั้งสองส่วนเข้าด้วยกัน ***
            # ต้อง reshape engineered_features ให้เป็น 2D array
            combined_features = hstack([tfidf_features, engineered_features.reshape(1, -1)])
            
            # 5. ทำนายความน่าจะเป็น
            # คะแนนความเสี่ยงคือความน่าจะเป็นที่จะเป็น Phishing (class 1)
            risk_score = self.model.predict_proba(combined_features)[0][1]

            # สร้าง dictionary ของ features เพื่อแสดงผล
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

    # generate_recommendations, save_model, load_model, และฟังก์ชันอื่นๆ เหมือนเดิม
    # ... (คัดลอกฟังก์ชันที่เหลือจากโค้ดเดิมมาวางตรงนี้) ...
    def load_dataset(self, file_path):
        """
        โหลด dataset จากไฟล์ต่างๆ (CSV, Excel, หรือ text)
        """
        try:
            # หาตำแหน่งไฟล์ที่เป็นไปได้
            possible_paths = [
                file_path,  # path ที่ระบุมาโดยตรง
                os.path.join(os.getcwd(), file_path),  # current working directory
            ]

            actual_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    actual_path = path
                    break

            if actual_path is None:
                raise FileNotFoundError(f"ไม่พบไฟล์ {file_path}")

            print(f"พบไฟล์ที่: {actual_path}")

            # ตรวจสอบนามสกุลไฟล์
            file_extension = os.path.splitext(actual_path)[1].lower()

            if file_extension == '.csv':
                # ลองหลาย encoding
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
                    raise ValueError("ไม่สามารถอ่านไฟล์ CSV ได้ ลองเปลี่ยน encoding")
            # ... ส่วนที่เหลือของ load_dataset ...
            else:
                raise ValueError(f"ไม่รองรับไฟล์นามสกุล {file_extension}")
            return df
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