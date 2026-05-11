from rest_framework import serializers
from .models import *
import re

# class Signup_serilizer(serializers.ModelSerializer):
#     class Meta:
#         model=User
#         fields=["first_name","last_name","email","password","phone"]



#     def validate_password(self,value):
#         if len(value)<8:
#             raise serializers.ValidationError("password must be of 8 characters")
        
#         if not re.search(r'[A-Z]',value):
#             raise serializers.ValidationError("password must contain uppercase character")
        
#         if not re.search(r'[a-z]',value):
#             raise serializers.ValidationError("password must contain lowercase character")
        
#         if not re.search(r'[0-9]',value):
#              raise serializers.ValidationError("password must contain digits")
        
#         if not re.search(r'[!@#$%^&*]',value):
#               raise serializers.ValidationError("password must contain special character")
#         return value


#     def create(self, validated_data):
#         user = User(
#         first_name=validated_data.get('first_name'),
#         last_name=validated_data.get('last_name'),
#         email=validated_data.get('email'),
#         phone=validated_data.get('phone')
#     )
#         user.set_password(validated_data.get('password'))
#         user.save()
#         return user


from rest_framework import serializers
from .models import *

class Srapi(serializers.ModelSerializer):
    class Meta:
        model=Productapi
        fields= '__all__'