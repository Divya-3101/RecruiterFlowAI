from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/',blank=True,null=True)
    resume = models.FileField(upload_to='resumes/',blank=True,null=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return self.user.username

