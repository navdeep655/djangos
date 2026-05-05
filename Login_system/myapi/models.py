from django.db import models

# Create your models here.
class Productapi(models.Model):
    name=models.CharField(max_length=20)
    price=models.IntegerField()

    def __str__(self):
        return self.name


class staff(models.Model):
    name=models.CharField(max_length=20)
    email=models.EmailField()
    number=models.IntegerField()
