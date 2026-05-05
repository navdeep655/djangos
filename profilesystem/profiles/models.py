from django.db import models

# Create your models here.
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


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
   
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    # phone = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)    
    image = models.ImageField(upload_to='profile_images/',null=True,blank=True
)


    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"