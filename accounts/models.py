from django.db import models

# Create your models here.
class customeModel(models.Model):
    name=models.CharField(max_length=200,null=True)
    email=models.EmailField(max_length=200,null=True)
    role=models.CharField(max_length=200,null=True)
    