from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmailAnalysis, Report, SystemEvaluation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class EmailAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAnalysis
        fields = ['id', 'content', 'risk_score', 'analyzed_at']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'recommendations', 'generated_at']

class SystemEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemEvaluation
        fields = ['accuracy', 'usability', 'speed', 'reliability', 'overall', 'comments']