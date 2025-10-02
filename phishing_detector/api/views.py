from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import EmailAnalysis, Report, SystemEvaluation
from .serializers import (UserSerializer, EmailAnalysisSerializer,
                          ReportSerializer, SystemEvaluationSerializer)
from .phishing_detector import phishing_detector

# --- เพิ่มส่วนของ Google Login ---
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    """
    View สำหรับจัดการการ Login ผ่าน Google
    รับ access_token จาก frontend แล้วส่งต่อไปยัง allauth เพื่อตรวจสอบ
    จากนั้น dj-rest-auth จะสร้าง JWT token ของแอปเราให้
    """
    adapter_class = GoogleOAuth2Adapter
    # callback_url ต้องตรงกับที่ตั้งค่าใน Google Console (ส่วนใหญ่เป็น URL ของ frontend)
    callback_url = "http://localhost:3000" # หรือ 5173 ตาม port ของคุณ
    client_class = OAuth2Client

# ------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'กรุณากรอกอีเมลและรหัสผ่าน'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=email).exists():
            return Response({'error': 'อีเมลนี้ถูกใช้งานแล้ว'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        return Response({'message': 'ลงทะเบียนสำเร็จ'},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'เกิดข้อผิดพลาดในการลงทะเบียน: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------
# --- ฟังก์ชันอื่นๆ ด้านล่างนี้ ไม่ต้องแก้ไข ---
# ---------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_email(request):
    # ... โค้ดเดิม ...
    try:
        content = ""
        
        if request.data.get('type') == 'text':
            content = request.data.get('content', '')
        elif request.data.get('type') == 'file':
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({'error': 'ไม่พบไฟล์ที่อัปโหลด'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            if not uploaded_file.name.endswith('.eml'):
                return Response({'error': 'กรุณาอัปโหลดไฟล์ .eml เท่านั้น'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            try:
                file_content = uploaded_file.read()
                content = phishing_detector.parse_eml_file(file_content)
            except ValueError as e:
                return Response({'error': str(e)}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        if not content.strip():
            return Response({'error': 'เนื้อหาอีเมลว่างเปล่า'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Analyze the email
        analysis_result = phishing_detector.analyze_email(content)
        
        # Save analysis to database
        email_analysis = EmailAnalysis.objects.create(
            user=request.user,
            content=content,
            risk_score=analysis_result['risk_score']
        )
        
        # Create report
        report = Report.objects.create(
            email_analysis=email_analysis,
            recommendations='\n'.join(analysis_result['recommendations'])
        )
        
        return Response({
            'id': email_analysis.id,
            'risk_score': analysis_result['risk_score'],
            'recommendations': analysis_result['recommendations'],
            'details': analysis_result.get('details', {})
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': f'เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_history(request):
    # ... โค้ดเดิม ...
    try:
        analyses = EmailAnalysis.objects.filter(user=request.user)
        serializer = EmailAnalysisSerializer(analyses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': 'เกิดข้อผิดพลาดในการโหลดข้อมูล'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    # ... โค้ดเดิม ...
    try:
        user_analyses = EmailAnalysis.objects.filter(user=request.user)
        
        total_emails = user_analyses.count()
        phishing_detected = user_analyses.filter(risk_score__gte=0.4).count()
        safe_emails = user_analyses.filter(risk_score__lt=0.4).count()
        
        accuracy = 95.2  # Mock accuracy
        
        return Response({
            'totalEmails': total_emails,
            'phishingDetected': phishing_detected,
            'safeEmails': safe_emails,
            'accuracy': accuracy
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': 'เกิดข้อผิดพลาดในการโหลดสถิติ'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    # ... โค้ดเดิม ...
    try:
        user = request.user
        email = request.data.get('email')
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')
        
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response({'error': 'อีเมลนี้ถูกใช้งานแล้ว'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            user.email = email
            user.username = email
        
        if new_password:
            if not current_password:
                return Response({'error': 'กรุณากรอกรหัสผ่านปัจจุบัน'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            if not user.check_password(current_password):
                return Response({'error': 'รหัสผ่านปัจจุบันไม่ถูกต้อง'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
        
        user.save()
        
        return Response({'message': 'อัปเดตข้อมูลสำเร็จ'}, 
                        status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': 'เกิดข้อผิดพลาดในการอัปเดตข้อมูล'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_evaluation(request):
    # ... โค้ดเดิม ...
    try:
        serializer = SystemEvaluationSerializer(data=request.data)
        if serializer.is_valid():
            evaluation = serializer.save(user=request.user)
            return Response({'message': 'ส่งการประเมินสำเร็จ'}, 
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': 'เกิดข้อผิดพลาดในการส่งการประเมิน'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
