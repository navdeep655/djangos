from rest_framework import serializers
from .models import User, UserProfile
import re

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "phone"]

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain an uppercase character")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain a lowercase character")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain a digit")
        if not re.search(r'[!@#$%^&*]', value):
            raise serializers.ValidationError("Password must contain a special character")
        return value

    def create(self, validated_data):
        user = User(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class LoginSerializer(serializers.Serializer): 
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    phone = serializers.CharField(source="user.phone")
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'phone', 'gender', 'pincode', 'city', 'state','country', 'address', 'date_of_birth', 'image','full_name']

    def update(self, instance, validated_data):  
        # Nested user data 
        user_data = validated_data.pop('user', {})
        user = instance.user

        # User fields update 
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.phone = user_data.get('phone', user.phone)
        user.save()

        # UserProfile fields update 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance