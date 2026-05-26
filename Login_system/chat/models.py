from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class chat_user(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic=models.ImageField(upload_to='images/',blank=True,null=True)
    age=models.CharField(max_length=3)
    gender_choice=[('M',"M"),("F","F"),]
    gender=models.CharField(max_length=1,choices=gender_choice)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
 

class chatroomr(models.Model):
    name=models.CharField(max_length=30,null=True,blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,related_name="roomowner",null=True,blank=True)
    members = models.ManyToManyField(User,"member",null=True,blank=True)
    max_members = models.IntegerField(default=2,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    room=models.ForeignKey(chatroomr,on_delete=models.CASCADE,related_name="room")
    message_sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name="message_sender")
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)

class JoinRequest(models.Model):
    room_name=models.ForeignKey(chatroomr,on_delete=models.CASCADE,related_name="room_name")
    sender_name=models.ForeignKey(User,on_delete=models.CASCADE,related_name="sender_name")
    status_request=[('pending','pending'),
                    ('accepted','accepted'),
                    ('rejected','rejected')]
    status=models.CharField(max_length=10,choices=status_request)
    request_send_at=models.DateTimeField(auto_now_add=True)


