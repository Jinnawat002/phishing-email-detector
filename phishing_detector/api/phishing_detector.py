import re
import os
import email
import pickle
from urllib.parse import urlparse

import nltk
import numpy as np
import pandas as pd

# --- ADDED ---: เพิ่ม import สำหรับ Hugging Face Datasets
from datasets import load_dataset
# -------------

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

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
            'ด่วน', 'ยืนยัน', 'คลิกที่นี่', 'ฟรี', 'รางวัล', 'หมดเวลา',
            'อัปเดต', 'แจ้งเตือน', 'ระงับ', 'ยกเลิก'
        ]

        self.suspicious_domains = [
            'bit.ly', 'tinyurl.com', 't.co', 'goo.gl',
            'shortened.link', 'short.link'
        ]

        # Initialize vectorizer and model
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model = MultinomialNB()
        self.is_trained = False

    def load_dataset(self, file_path):
        """
        โหลด dataset จากไฟล์ต่างๆ (CSV, Excel, หรือ text)
        """
        try:
            # หาตำแหน่งไฟล์ที่เป็นไปได้
            possible_paths = [
                file_path,  # path ที่ระบุมาโดยตรง
                os.path.join(os.getcwd(), file_path),  # current working directory
                os.path.join(os.path.dirname(__file__), file_path),  # same directory as this file
                os.path.join(os.path.dirname(__file__), '..', file_path),  # parent directory
                os.path.join(os.path.dirname(__file__), 'data', file_path),  # data subdirectory
                os.path.join(os.path.dirname(__file__), '..', 'data', file_path),  # data in parent
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

            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(actual_path)
            elif file_extension == '.txt':
                with open(actual_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                data = []
                for line in lines:
                    parts = line.strip().split(',', 1)
                    if len(parts) == 2:
                        data.append({'label': int(parts[0]), 'email': parts[1]})
                df = pd.DataFrame(data)
            else:
                raise ValueError(f"ไม่รองรับไฟล์นามสกุล {file_extension}")

            print(f"โหลดข้อมูลสำเร็จ: {len(df)} รายการ")
            return df

        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
            return None

     # --- NEW FUNCTION (Cleaned up) ---
    def preprocess_data(self, df):
        """
        เตรียมข้อมูลสำหรับการเทรน (ฉบับสมบูรณ์)
        """
        try:
            # ณ จุดนี้ df ควรมีแค่คอลัมน์ 'email' และ 'label' แล้ว
            df.dropna(subset=['email', 'label'], inplace=True)
            
            # ตรวจสอบชนิดข้อมูลของคอลัมน์ label
            if df['label'].dtype == 'object':
                label_map = {
                    'Phishing Email': 1, 'Safe Email': 0, # จากไฟล์ CSV
                    'phishing': 1, 'Phishing': 1, 'PHISHING': 1,
                    'safe': 0, 'Safe': 0, 'SAFE': 0,
                    'legitimate': 0, 'Legitimate': 0, 'LEGITIMATE': 0,
                }
                # ใช้ .map สำหรับค่าที่เป็นข้อความ
                df['label'] = df['label'].map(label_map)

            # แปลงทุกอย่างในคอลัมน์ label ให้เป็นตัวเลข และลบแถวที่แปลงไม่ได้
            df['label'] = pd.to_numeric(df['label'], errors='coerce')
            df.dropna(subset=['label'], inplace=True)
            df['label'] = df['label'].astype(int)

            print(f"ข้อมูลหลังการเตรียม: {len(df)} รายการ")
            print(f"การกระจายของ label: \n{df['label'].value_counts()}")

            return df['email'].astype(str).tolist(), df['label'].tolist()

        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาดในการเตรียมข้อมูล: {str(e)}")
            traceback.print_exc()
            return None, None

    def find_dataset_file(self, filename="Phishing_Email.csv"):
        """
        ค้นหาไฟล์ dataset ในตำแหน่งที่เป็นไปได้
        """
        search_paths = [
            filename,
            os.path.join(os.path.dirname(__file__), filename),
            os.path.join(os.path.dirname(__file__), '..', filename),
            os.path.join('data', filename),
            os.path.join(os.path.dirname(__file__), 'data', filename),
            os.path.join(os.path.dirname(__file__), '..', 'data', filename),
        ]
        print(f"กำลังค้นหาไฟล์ {filename}...")
        for path in search_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                print(f"พบไฟล์ที่: {abs_path}")
                return abs_path
        print(f"ไม่พบไฟล์ {filename} ในตำแหน่งใดๆ")
        return None

    # --- NEW FUNCTION (FIXED) ---
    def train_with_combined_data(self, local_csv_path=None, test_size=0.2, save_model=True):
        """
        เทรนโมเดลโดยใช้ข้อมูลจากไฟล์ CSV เดิมและ Dataset จาก Hugging Face (ฉบับแก้ไข)
        """
        print("===== เริ่มกระบวนการเทรนโมเดลด้วยข้อมูลผสม =====")

        # --- 1. โหลดและเตรียมข้อมูลจากไฟล์ CSV เดิม ---
        print("\n[ขั้นตอนที่ 1/4] กำลังโหลดและเตรียมข้อมูลจากไฟล์ CSV...")
        df_local = pd.DataFrame()
        if local_csv_path is None:
            local_csv_path = self.find_dataset_file("Phishing_Email.csv")
        
        if local_csv_path:
            loaded_df = self.load_dataset(local_csv_path)
            if loaded_df is not None and 'Email Text' in loaded_df and 'Email Type' in loaded_df:
                # เลือกเฉพาะคอลัมน์ที่ต้องการและ rename ทันที
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
            hf_dataset = load_dataset("kmack/Phishing_urls", split='train') # เลือกเฉพาะ split 'train'
            df_hf_all = hf_dataset.to_pandas()
            if 'text' in df_hf_all and 'label' in df_hf_all:
                # เลือกเฉพาะคอลัมน์ที่ต้องการและ rename ทันที
                df_hf = df_hf_all[['text', 'label']].rename(columns={'text': 'email'})
                print(f"เตรียมข้อมูลจาก Hugging Face สำเร็จ: {len(df_hf)} รายการ")
            else:
                 print("Dataset จาก Hugging Face ไม่พบคอลัมน์ที่คาดหวัง ('url', 'label')")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการดาวน์โหลดข้อมูลจาก Hugging Face: {e}")

        # --- 3. รวมข้อมูลที่เตรียมแล้ว ---
        print("\n[ขั้นตอนที่ 3/4] กำลังรวมข้อมูลที่จัดรูปแบบแล้ว...")
        if not df_local.empty or not df_hf.empty:
            combined_df = pd.concat([df_local, df_hf], ignore_index=True)
            print(f"ขนาดข้อมูลรวมทั้งหมด: {len(combined_df)} รายการ")
            print(f"ตัวอย่างข้อมูลหลังรวม:\n{combined_df.head().to_string()}")
        else:
            print("ไม่สามารถโหลดข้อมูลจากแหล่งใดได้เลย สิ้นสุดการเทรน")
            return False

        # --- 4. เตรียมข้อมูลขั้นสุดท้ายและเทรนโมเดล ---
        print("\n[ขั้นตอนที่ 4/4] กำลังเตรียมข้อมูลขั้นสุดท้ายและเทรนโมเดล...")
        texts, labels = self.preprocess_data(combined_df)
        if texts is None or labels is None:
            return False

        try:
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=test_size, random_state=42, stratify=labels
            )
            print(f"ข้อมูลการเทรน: {len(X_train)} รายการ, ข้อมูลการทดสอบ: {len(X_test)} รายการ")

            X_train_tfidf = self.vectorizer.fit_transform(X_train)
            X_test_tfidf = self.vectorizer.transform(X_test)
            self.model.fit(X_train_tfidf, y_train)
            
            y_pred = self.model.predict(X_test_tfidf)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"\nผลการเทรน:\nAccuracy: {accuracy:.4f}")
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))
            
            self.is_trained = True
            if save_model:
                self.save_model()
            return True
        except Exception as e:
            import traceback
            print(f"เกิดข้อผิดพลาดในการเทรนโมเดล: {str(e)}")
            traceback.print_exc()
            return False

    def save_model(self, model_path='phishing_model.pkl', vectorizer_path='tfidf_vectorizer.pkl'):
        """
        บันทึกโมเดลและ vectorizer
        """
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            print(f"บันทึกโมเดลสำเร็จที่: {model_path} และ {vectorizer_path}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการบันทึกโมเดล: {str(e)}")

    def load_model(self, model_path='phishing_model.pkl', vectorizer_path='tfidf_vectorizer.pkl'):
        """
        โหลดโมเดลและ vectorizer ที่บันทึกไว้
        """
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
        
    def parse_eml_file(self, file_content):
        """
        อ่านและดึงเนื้อหาที่เป็น text จากไฟล์ .eml
        """
        try:
            # แปลง bytes ที่ได้รับจากไฟล์อัปโหลดเป็น string ก่อน
            # และใช้ message_from_string เพื่อประมวลผล
            msg = email.message_from_string(file_content.decode('utf-8', errors='ignore'))

            # วนลูปเพื่อหาเนื้อหาที่เป็น text/plain
            if msg.is_multipart():
                content = ""
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # เอาเฉพาะส่วนที่เป็น text และไม่ใช่ไฟล์แนบ
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            # ลอง decode ด้วย charset ที่ระบุใน email ก่อน
                            charset = part.get_content_charset() or 'utf-8'
                            content += part.get_payload(decode=True).decode(charset, errors='ignore')
                        except (LookupError, AttributeError):
                            # ถ้าหา charset ไม่เจอ หรือมีปัญหาอื่น ให้ใช้ utf-8 เป็น fallback
                            content += part.get_payload(decode=True).decode('utf-8', errors='ignore')

                # ถ้าวนลูปแล้วไม่เจอ text/plain เลย ให้ลองหา text/html แทน
                if not content:
                     for part in msg.walk():
                        if part.get_content_type() == "text/html":
                             # (ในอนาคตอาจเพิ่มการ clean HTML tag ตรงนี้ได้)
                             content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                return content
            
            else:
                # กรณีที่อีเมลไม่มี multipart (เป็น text ธรรมดา)
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        except Exception as e:
            raise ValueError(f"ไม่สามารถอ่านไฟล์ .eml ได้: {str(e)}")
            
    # --- ส่วนที่เหลือของคลาส (analyze_email, extract_features etc.) เหมือนเดิม ---
    # (คัดลอกฟังก์ชันที่เหลือจากโค้ดเดิมของคุณมาวางตรงนี้ได้เลย)
    def extract_features(self, content):
        features = {}
        keyword_count = sum(1 for keyword in self.suspicious_keywords if keyword.lower() in content.lower())
        features['keyword_score'] = min(keyword_count / 5, 1.0)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        suspicious_url_count = sum(1 for url in urls if any(sus_domain in urlparse(url).netloc for sus_domain in self.suspicious_domains))
        features['url_score'] = min(suspicious_url_count / 3, 1.0)
        urgency_count = sum(1 for word in ['urgent', 'immediate', 'asap', 'expire', 'ด่วน', 'เร่งด่วน'] if word.lower() in content.lower())
        features['urgency_score'] = min(urgency_count / 3, 1.0)
        personal_info_count = sum(1 for keyword in ['password', 'ssn', 'credit card', 'bank account', 'รหัสผ่าน', 'บัตรเครดิต', 'บัญชีธนาคาร'] if keyword.lower() in content.lower())
        features['personal_info_score'] = min(personal_info_count / 2, 1.0)
        return features

    def analyze_email(self, content):
        if not self.is_trained:
            print("โมเดลยังไม่ได้เทรน กำลังใช้การวิเคราะห์แบบ Rule-based")
            return self._fallback_analysis(content)
        try:
            features = self.extract_features(content)
            X = self.vectorizer.transform([content])
            ml_probability = self.model.predict_proba(X)[0][1]
            feature_score = sum(features.values()) / len(features)
            final_score = (ml_probability * 0.7) + (feature_score * 0.3)
            recommendations = self.generate_recommendations(final_score, features)
            return {'risk_score': float(final_score), 'features': features, 'recommendations': recommendations}
        except Exception as e:
            return self._fallback_analysis(content, str(e))

    def _fallback_analysis(self, content, error_msg=None):
        features = self.extract_features(content)
        feature_score = sum(features.values()) / len(features)
        recommendations = self.generate_recommendations(feature_score, features)
        if error_msg:
            recommendations.insert(0, f'หมายเหตุ: เกิดข้อผิดพลาด ({error_msg})')
        return {'risk_score': float(feature_score), 'features': features, 'recommendations': recommendations, 'note': 'ใช้การวิเคราะห์แบบ rule-based เท่านั้น'}

    def generate_recommendations(self, score, features):
        recommendations = []
        if score >= 0.7:
            recommendations.extend(['ความเสี่ยงสูงมาก', 'ไม่ควรคลิกลิงก์หรือให้ข้อมูลส่วนตัว', 'ลบอีเมลนี้ทิ้ง'])
        elif score >= 0.5:
            recommendations.extend(['ความเสี่ยงสูง', 'ตรวจสอบผู้ส่งและลิงก์อย่างระมัดระวัง'])
        elif score >= 0.3:
            recommendations.extend(['ความเสี่ยงปานกลาง', 'โปรดใช้ความระมัดระวัง'])
        else:
            recommendations.extend(['ความเสี่ยงต่ำ', 'น่าจะปลอดภัย แต่ควรตรวจสอบเสมอ'])
        if features.get('url_score', 0) > 0:
            recommendations.append('พบลิงก์ที่อาจเป็น URL ย่อส่วน ควรตรวจสอบให้ดีก่อนคลิก')
        return recommendations

# สร้าง instance สำหรับใช้ใน Django
phishing_detector = PhishingDetector()


def initialize_model():
    """
    เริ่มต้นโมเดล: ลองโหลดโมเดลที่บันทึกไว้ ถ้าไม่เจอก็จะเทรนใหม่จาก dataset ผสม
    """
    print("Initializing Phishing Detector Model...")
    # ลองโหลดโมเดลที่บันทึกไว้ก่อน
    if phishing_detector.load_model():
        print("Model loaded successfully from saved files.")
        return True

    # ถ้าโหลดไม่สำเร็จ ให้เทรนใหม่โดยใช้ข้อมูลผสม
    print("\nCould not find saved model. Starting training process with combined data...")
    if phishing_detector.train_with_combined_data():
        print("\nNew model trained and saved successfully!")
    else:
        print("\nFailed to train the model. The detector will rely on rule-based analysis only.")
        # โมเดลจะอยู่ในสถานะ is_trained = False และจะใช้ _fallback_analysis()
    return True

# --- MODIFIED ---: แก้ไขฟังก์ชัน train_model_from_dataset
def train_model_from_dataset(force_retrain=False):
    """
    ฟังก์ชันสำหรับเทรนโมเดลใหม่จาก dataset ผสม (สำหรับเรียกใช้ผ่าน API หรือ command line)
    """
    global phishing_detector
    if phishing_detector.is_trained and not force_retrain:
        print("โมเดลถูกเทรนแล้ว หากต้องการเทรนใหม่ให้ใช้ force_retrain=True")
        return True

    print("Forcing model retraining with combined dataset...")
    if phishing_detector.train_with_combined_data():
        print("Retraining successful!")
        return True
    else:
        print("Retraining failed.")
        return False


def test_model():
    """ ทดสอบโมเดลด้วยข้อมูลตัวอย่าง """
    if not phishing_detector.is_trained:
        print("\nไม่สามารถทดสอบโมเดลได้ เนื่องจากยังไม่ได้เทรน")
        return
        
    print("\n" + "="*50)
    print("Testing model with sample data...")
    test_cases = [
        'Urgent! Your account has been suspended. Click here to verify: http://bit.ly/fake-link',
        'Thank you for your purchase. Your order #12345 has been confirmed.',
        'Congratulations! You have won $10000. Claim now: http://short.link/prize',
        'http://secure-login-apple-support.com/info' # ตัวอย่าง URL จาก Hugging Face
    ]
    for text in test_cases:
        result = phishing_detector.analyze_email(text)
        print(f"\nText: {text[:60]}...")
        print(f"Risk Score: {result['risk_score']:.3f}")
        print(f"Recommendations: {', '.join(result['recommendations'])}")
    print("="*50)

# Example usage for running this file directly
if __name__ == "__main__":
    print("Running phishing_detector.py as a standalone script.")
    
    #เทรนโมเดล (ถ้ายังไม่มีไฟล์ .pkl มันจะถูกสร้างขึ้น)
    train_model_from_dataset(force_retrain=True)

    #ทดสอบโมเดลที่เพิ่งเทรนไป
    test_model()