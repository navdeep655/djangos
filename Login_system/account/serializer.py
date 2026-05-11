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
    
class product_serializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields="__all__"



class profile_serializer(serializers.ModelSerializer):
    username=serializers.CharField(source="user.username",read_only=True)
    first_name=serializers.CharField(source="user.first_name")
    last_name=serializers.CharField(source="user.last_name")
    email=serializers.EmailField(source="user.email",read_only=True)
    class Meta:
        model=profile_data
        fields=["username","first_name","last_name","email","image","phone","address"]

    def update(self,instance,validated_data):
        instance.user.first_name=validated_data["user"]["first_name"]
        instance.user.last_name=validated_data["user"]["last_name"]
        instance.user.save()
        instance.image = validated_data.get("image", instance.image)
        instance.phone=validated_data["phone"]
        instance.address=validated_data["address"]
        instance.save()
        return instance

class cart_serializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(source="user.id",read_only=True)
    product_id=serializers.IntegerField(source="product.id",read_only=True)
    product_name = serializers.CharField(source='product.name',read_only=True)
    product_image = serializers.ImageField(source='product.image',read_only=True)
    product_price=serializers.IntegerField(source='product.price',read_only=True)
    class Meta:
        model=Cart
        fields=fields = ["id",'user_id','product_id','product_name','product_image', 'product_price','quantity']

    def validate(self, data):
        user = data.get('user')
        product = data.get('product')

        if Cart.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError("Product already in cart")
        return data


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"
        read_only_fields = ["user"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

    



















