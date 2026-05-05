from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout as django_logout
from rest_framework.views import APIView
from .models import *
from .serializer import *
from .dacoratorsjwt import jwt_required


class SignupApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            UserProfile.objects.create(user=user)
            return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
                response.set_cookie( key='access_token',value=str(refresh.access_token),httponly=True,samesite='Lax')
                return response


class LogoutApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # token blacklist 

            response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')  #cookie clear 
            django_logout(request)
            return response

        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [AllowAny]  #  AllowAny → IsAuthenticated

    def get(self, request):  #  GET method add kiya - pre-filled data
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        



from django.shortcuts import render

def signup_page(request):
    return render(request, 'profile/signup.html')

def login_page(request):
    return render(request, 'profile/login.html')
@jwt_required
def dashboard_page(request):
    return render(request, 'profile/dashboard.html')
@jwt_required
def profile_page(request):
    return render(request, 'profile/profile.html')