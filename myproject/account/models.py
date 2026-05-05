from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    fullname=models.CharField(max_length=20)
    GENDER_CHOICES = [('M', 'Male'),('F', 'Female')]
    gender=models.CharField(choices=GENDER_CHOICES)
    city=models.CharField(max_length=20)
    phone=models.CharField(max_length=10)

