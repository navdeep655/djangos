from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.paginator import Paginator
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from.dacoratorjwt import jwt_required
from .authentication import *
from rest_framework.parsers import JSONParser
# Create your views here.
class signupapi(APIView):
        permission_classes=[AllowAny]
        authentication_classes = []
        def post(self,request):
            serializer=signup_serializer(data=request.data)
            if serializer.is_valid():
                user=serializer.save()
                return Response({'message':"succesfull"})
            return Response(serializer.errors)

class signinapi(APIView):
    permission_classes=[AllowAny]
    authentication_classes = []
    def post(self,request):
        serializer=signin_serializer(data=request.data)
        if serializer.is_valid():
            username=serializer.validated_data["username"]
            password=serializer.validated_data["password"]
            user=authenticate(request,username=username,password=password)
            if user is not None:
                refresh=RefreshToken.for_user(user)
                response= Response({"refresh": str(refresh),"access":str(refresh.access_token),"message":"successfull login"})
                response.set_cookie(key="access_token",value=str(refresh.access_token),httponly=True,samesite='LAX')
                response.set_cookie(key="refresh_token", value=str(refresh), httponly=True, samesite='LAX')
                return response

            else:
                return Response({"error":"Invalid credentials"}, status=400)
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

class logoutapi(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes=[AllowAny]

    def post(self,request):
        refreshtoken=request.COOKIES.get("refresh_token")
        if not refreshtoken :
            return Response({"error":"refreshtoken required"})
        token=RefreshToken(refreshtoken)
        token.blacklist()
        response=Response({"message":"logout succesfully"})
        response.delete_cookie('access_token')
        response.delete_cookie("refresh_token")
        return response




def auth(request):
    return render(request, 'chat/chat_auth.html')

from django.db.models import Q

@jwt_required
def dashboard(request):
    rooms = chatroomr.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    return render(request, 'chat/dashboard.html', {'rooms': rooms,'user': request.user})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse

@jwt_required
def chat_room(request, room_id):
    room = get_object_or_404(chatroomr, id=room_id)
    is_owner = room.owner == request.user
    pending_requests = []
    if is_owner:
        pending_requests = JoinRequest.objects.filter(
            room_name=room,
            status="pending"
        ).select_related("sender_name")
    old_messages = Message.objects.filter(
        room=room
    ).select_related("message_sender").order_by("timestamp")

    return render(request, 'chat/room.html', {
        "room":             room,
        "is_owner":         is_owner,
        "pending_requests": pending_requests,
        "old_messages":     old_messages,
    })


class create_room(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    def post(self,request):
        serializer=room_serializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(owner=request.user)
            room.members.add(request.user)
            return Response({"message":"room_created", "room_id": room.id})
        return Response(serializer.errors, status=400)
    
    def delete(self,request,room_id):
        room=chatroomr.objects.get(id=room_id,owner=request.user)
        room.delete()
        return Response({"meassgae": "deleted"},status=200)
    
class search_room(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        name = request.GET.get("name")
        if not name:
            return Response({"error": "please enter room name"},status=400)
        room_data = chatroomr.objects.filter(name__icontains=name)
        print(room_data)
        serializer = search_serializer(room_data,many=True)
        return Response({"message": "rooms fetched successfully", "data": serializer.data}, status=200)


class JoinRoomView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]


    def post(self, request, room_id):
        try:
            room = chatroomr.objects.get(id=room_id)
        except chatroomr.DoesNotExist:
            return Response({"error": "Room nahi mila"}, status=404)
 
        #  Owner hai → seedha enter
        if room.owner == request.user:
            room.members.add(request.user)
            return Response({"message": "direct_enter", "room_id": room_id})
 
        # Pehle se member hai → seedha enter
        if request.user in room.members.all():
            return Response({"message": "direct_enter", "room_id": room_id})
 
        #  Room full hai
        if room.members.count() >= room.max_members:
            return Response({"error": "Room full hai"}, status=400)
 
        #  Pehle se request bheja hua?
        existing = JoinRequest.objects.filter(
            room_name=room,sender_name=request.user).first()
 
        if existing:
            if existing.status == "pending":
                return Response({"message": "request_already_sent"})
            elif existing.status == "rejected":
                return Response({"error": "Tumhari request reject ho chuki hai"}, status=400)
            elif existing.status == "accepted":
                room.members.add(request.user)
                return Response({"message": "direct_enter", "room_id": room_id})
        # Naya request 
        JoinRequest.objects.create(room_name=room,sender_name=request.user,status="pending")
        return Response({"message": "request_sent"})
    

class PendingRequestsView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, room_id):
        try:
            room = chatroomr.objects.get(id=room_id, owner=request.user)
        except chatroomr.DoesNotExist:
            return Response({"error": "Room nahi mila ya tum owner nahi ho"}, status=404)
        pending = JoinRequest.objects.filter(room_name=room, status="pending")
        serializer = JoinRequestSerializer(pending, many=True)
        return Response({"requests": serializer.data})
    
class HandleRequestView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, request_id):
        try:
            # Sirf owner hi action le sakta hai
            join_req = JoinRequest.objects.get(id=request_id,room_name__owner=request.user)
        except JoinRequest.DoesNotExist:
            return Response({"error": "Request nahi mila"}, status=404)
        action = request.data.get("action")
        if action not in ["accepted", "rejected"]:
            return Response(
                {"error": "action 'accepted' ya 'rejected' hona chahiye"},status=400)
        join_req.status = action
        join_req.save()
        # Accept hua → member mein add karo
        if action == "accepted":
            join_req.room_name.members.add(join_req.sender_name)
            return Response({"message": f"{join_req.sender_name.username} ko room mein add kar diya"})
        return Response({"message": "Request reject kar di"})


class ChatProfileAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = getattr(user, "chat_user", None)

        if not profile:
            return Response({
                "username": user.username,
                "profile_pic": "",
                "age": "",
                "gender": "",
                "state": "",
                "country": "",
            })

        serializer = ChatProfileSerializer(
            profile,
            context={"request": request}
        )
        return Response(serializer.data)


 
 
    

