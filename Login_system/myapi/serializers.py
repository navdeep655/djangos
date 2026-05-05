from rest_framework import serializers
from .models import *

class Srapi(serializers.ModelSerializer):
    class Meta:
        model=Productapi
        fields= '__all__'


class staff_people(serializers.ModelSerializer):
    class Meta:
        model=staff
        fields="__all__"