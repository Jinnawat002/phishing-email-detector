from django.contrib import admin
from .models import EmailAnalysis, Report, Admin, SystemEvaluation

@admin.register(EmailAnalysis)
class EmailAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'risk_score', 'analyzed_at']
    list_filter = ['risk_score', 'analyzed_at']
    search_fields = ['user__email', 'content']
    readonly_fields = ['analyzed_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'email_analysis', 'generated_at']
    list_filter = ['generated_at']
    readonly_fields = ['generated_at']

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    readonly_fields = ['created_at']

@admin.register(SystemEvaluation)
class SystemEvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'overall', 'created_at']
    list_filter = ['overall', 'created_at']
    readonly_fields = ['created_at']