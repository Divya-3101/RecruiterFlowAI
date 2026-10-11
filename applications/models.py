from django.db import models
from django.conf import settings
from jobs.models import Job

# Create your models here.
class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='applications/')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    semantic_score = models.FloatField(null=True, blank=True)
    skill_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)
    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['candidate', 'job'],name='unique_candidate_job_application')]
    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"
    
class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'job'],name='unique_saved_job')]

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
