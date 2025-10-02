from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        ฟังก์ชันนี้จะถูกเรียกใช้โดย Django เมื่อแอปพลิเคชันพร้อมทำงาน
        เหมาะสำหรับกาารันโค้ดเริ่มต้น เช่น การโหลดโมเดล Machine Learning
        """
        print("API App is ready. Initializing Phishing Detector Model...")
        # นำเข้าฟังก์ชัน initialize_model จากไฟล์ของคุณ
        from .phishing_detector import initialize_model
        
        # เรียกใช้งานฟังก์ชันเพื่อโหลดหรือเทรนโมเดล
        initialize_model()