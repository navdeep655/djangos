from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework .pagination import PageNumberPagination


class Mypagination(PageNumberPagination):
    page_size=5
    page_size_query_param='paze_size'
    max_page_size=10

# Create your views here.
@api_view(['GET'])
def get_products(request):
    product=Productapi.objects.all()
    paginator=Mypagination()
    result_page=paginator.paginate_queryset(product,request)
    serial=Srapi(result_page,many=True)
    return paginator.get_paginated_response(serial.data)
    
    
@api_view(['POST'])
def post_product(request):
    serializer=Srapi(data=request.data,status=status.HTTP_201_CREATED)

    if serializer .is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def staff_view(request):
    data=request.data
    serializer=staff_people(data=data)

    if serializer .is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def my_view(request):
    data = request.data 
    return Response({
        "message": "Success!"
    })


