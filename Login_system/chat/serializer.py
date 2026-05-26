from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages

class signup_serializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["username","email","password"]

    def create(self,validated_data):
        user=User(
            username=validated_data.get("username"),
            email=validated_data.get("email")
        )

        user.set_password(validated_data.get("password"))
        user.save()
        return user
    

class signin_serializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)
    def validate(self, validated_data):
        username = validated_data.get("username")
        password = validated_data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Please enter userand password")
        
        return validated_data
    

class room_serializer(serializers.ModelSerializer):
    class Meta:
        model=chatroomr
        fields = ['name', 'max_members']

class search_serializer(serializers.ModelSerializer):
    current_room_count=serializers.SerializerMethodField()
   
    class Meta:
        model=chatroomr
        fields=['id','name','owner','max_members','current_room_count']

    def get_current_room_count(self, obj):
         return obj.members.count()
    

class JoinRequestSerializer(serializers.ModelSerializer):
 
    sender_username = serializers.CharField(source="sender_name.username", read_only=True)
    room = serializers.CharField(source="room_name.name",read_only=True)
 
    class Meta:
        model  = JoinRequest
        fields = ["id", "room", "sender_username", "status", "request_send_at"]


class ChatProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = chat_user
        fields = ["username", "profile_pic", "age", "gender", "state", "country"]

    def get_profile_pic(self, obj):
        if not obj.profile_pic:
            return ""

        request = self.context.get("request")
        url = obj.profile_pic.url

        if request:
            return request.build_absolute_uri(url)

        return url

