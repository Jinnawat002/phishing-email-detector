from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmailAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_analyses')
    content = models.TextField()
    risk_score = models.FloatField()
    analyzed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'TB_EmailAnalysis'
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return f'Analysis {self.id} - Risk: {self.risk_score}'

class Report(models.Model):
    email_analysis = models.OneToOneField(EmailAnalysis, on_delete=models.CASCADE)
    recommendations = models.TextField()
    generated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'TB_Report'
    
    def __str__(self):
        return f'Report for Analysis {self.email_analysis.id}'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'TB_Admin'
    
    def __str__(self):
        return f'Admin: {self.user.email}'

class SystemEvaluation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accuracy = models.IntegerField()
    usability = models.IntegerField()
    speed = models.IntegerField()
    reliability = models.IntegerField()
    overall = models.IntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'TB_SystemEvaluation'
    
    def __str__(self):
        return f'Evaluation by {self.user.email}'