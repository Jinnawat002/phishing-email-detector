from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import GoogleLogin # <-- import view ใหม่เข้ามา

urlpatterns = [
    # --- Authentication URLs ---
    path('register/', views.register, name='register'),
    
    # URL สำหรับ Login แบบปกติ (ขอ Access & Refresh Token)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # URL สำหรับขอ Access Token ใหม่โดยใช้ Refresh Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- URL ใหม่สำหรับ Google Login ---
    # เราจะจัดกลุ่ม URL ที่เกี่ยวกับ auth ไว้ด้วยกัน
    # Frontend จะต้องส่ง POST request มาที่ /api/auth/google/
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    
    # --- Other API URLs ---
    path('email/analyze/', views.analyze_email, name='analyze_email'),
    path('email/history/', views.email_history, name='email_history'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('evaluation/submit/', views.submit_evaluation, name='submit_evaluation'),
]