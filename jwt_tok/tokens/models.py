from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


# Create your models here.
class Productapi(models.Model):
    name=models.CharField(max_length=20)
    price=models.IntegerField()

    def __str__(self):
        return self.name