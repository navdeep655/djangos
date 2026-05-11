from django.shortcuts import render,redirect
from rest_framework .response import Response
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import *
from .serilaizer import *
from rest_framework import serializers
from rest_framework import status
from django.contrib.auth import authenticate,login,logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from rest_framework .pagination import PageNumberPagination
import time


# Create your views here.

# @api_view(["POST"])
# @permission_classes([AllowAny])
# def signup(request):
#     data=request.data
#     serializer=Signup_serilizer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def djlogin(request):
#     email = request.data.get("email")
#     password = request.data.get("password")
#     # 1. authenticate user
#     if not email or not password:
#         return Response({"error": "Please enter email and password"}, status=status.HTTP_400_BAD_REQUEST )
#     user = authenticate(username=email, password=password)
#     if user is None:   
#         return Response({"error": "Invalid credentials"})

#     # 2. generate tokens
#     refresh = RefreshToken.for_user(user)
#     login(request,user)
#     request.session['refresh_token'] = str(refresh) 
#     return Response({ "refresh": str(refresh),"access": str(refresh.access_token),})


# def signup_page(request):
#     return render(request, "tokens/signup.html")


# def login_page(request):
#     return render(request,"tokens/login.html")

# @login_required
# def dashboard(request):
#     return render(request,"tokens/dashboard.html")


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])  # sirf logged in user logout kar sakta
# def djlogout(request):
#     try:
#         # 1. Refresh token lo request se
#         refresh_token = request.data.get("refresh")

#         if not refresh_token:
#             return Response(
#                 {"error": "Refresh token do"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # 2. JWT token blacklist karo (block kar do)
#         token = RefreshToken(refresh_token)
#         token.blacklist()

#         # 3. Django session bhi destroy karo
#         django_logout(request)

#         return Response(
#             {"message": "Logout successful!"},
#             status=status.HTTP_200_OK
#         )
#     except Exception as e:
#         return Response(
#             {"error": "Invalid token"},
#             status=status.HTTP_400_BAD_REQUEST
#         )



class Mypagination(PageNumberPagination):
    page_size=5
    page_size_query_param='paze_size'
    max_page_size=10   

@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    time.sleep(1)
    product=Productapi.objects.all()
    paginator=Mypagination()
    result_page=paginator.paginate_queryset(product,request)
    serial=Srapi(result_page,many=True)
    return paginator.get_paginated_response(serial.data)


@api_view(["PUT"])
@permission_classes([AllowAny])
def update(request,product_id):
        try:
            product=Productapi.objects.get(id=product_id)

        except:
            return Response({"error":"not found"},status=404)
        
        serializer=Srapi(product,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_any(request,product_id):
    try:
        product=Productapi.objects.get(id=product_id)
        print(product)
    except:
        return Response({"error":"valid"},status=404)
    serializer=Srapi(product,data=request.data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete(request,product_id):
    try:
        product=Productapi.object.get(id=product_id)
    except:
        return Response({"error":"not valid"},status=404)
    product.delete()
    return Response({"message": "Deleted successfully"}, status=204)


#genric api

from rest_framework.generics import RetrieveUpdateDestroyAPIView,ListAPIView
class Productview(RetrieveUpdateDestroyAPIView):
    queryset=Productapi.objects.all()
    serializer_class=Srapi


# class view api
from rest_framework.views import APIView
class ProductDetailAPIView(APIView):

    def get(self, request, pk=None):
        if not pk:
            product = Productapi.objects.all()
            serializer = Srapi(product,many=True)
            return Response(serializer.data)
        else:
            product = Productapi.objects.get(pk=pk)
            serializer = Srapi(product)
            return Response(serializer.data)


    def put(self, request, pk):
        product = Productapi.objects.get(pk=pk)
        serializer = Srapi(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, pk):
        product = Productapi.objects.get(pk=pk)
        product.delete()
        return Response({"msg": "deleted"})
    




# view set api

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
class productviewset(ModelViewSet):
    queryset=Productapi.objects.all()
    serializer_class=Srapi
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'price']

    # permission_classes = [IsAuthenticated]

    @action(detail=False,methods=["GET"])
    def recent(self,request):
        product=Productapi.objects.order_by('-id')
        serializer = Srapi(product, many=True)
        return Response(serializer.data)



#filter
from rest_framework.filters import SearchFilter
class searchfilter(ModelViewSet):
    queryset=Productapi.objects.all()
    serializer_class=Srapi
    filter_backends=[SearchFilter]
    search_fields=["name"]



#genric api
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin ,ListModelMixin 

class ProductView(ListModelMixin,CreateModelMixin,GenericAPIView):
    queryset = Productapi.objects.all()
    serializer_class = Srapi

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)