from django.db import models
from django.conf import settings


class Job(models.Model):
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    salary = models.IntegerField()
    description = models.TextField()
    required_skills = models.TextField(help_text="Enter skills separated by commas")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_skills_list(self):
        """
        Returns list of required skills cleaned and stripped.
        """
        if not self.required_skills:
            return []
        skills_text = self.required_skills.replace(';', ',').replace('\n', ',')
        return [
            skill.strip()
            for skill in skills_text.split(',')
            if skill.strip()
        ]