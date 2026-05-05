from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
# Create your models here.
class User(AbstractUser):
    email=models.EmailField(unique=True)
    username=models.CharField(blank=True,null=True,max_length=255)
    phone = models.CharField(blank=True, null=True, max_length=15)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects = UserManager() 


from django.db import models

# Create your models here.
class Productapi(models.Model):
    name=models.CharField(max_length=20)
    price=models.IntegerField()

    def __str__(self):
        return self.name