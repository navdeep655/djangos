

from django.urls import path
from .views import *

urlpatterns = [
    path('auth/', auth, name='authlogin'),
    path("signup/api/",signupapi.as_view(),name="signupapi"),
    path("login/api/",signinapi.as_view(),name="loginapi"),
    path("room/api/",create_room.as_view(),name="room"),
    path("logout/api/",logoutapi.as_view(),name="logoutapi"),
    path('createroom/api/',create_room.as_view(), name='create_room'),
    path('deleteroom/<int:room_id>/', create_room.as_view(), name='delete_room'),
    path('searchroom/api/', search_room.as_view()),
    path("room/join/<int:room_id>",JoinRoomView.as_view()),
    path("room/requests/<int:room_id>/",PendingRequestsView.as_view()),
    path("joinrequest/action/<int:request_id>/",  HandleRequestView.as_view()),
    path("profile/api/<str:username>/", ChatProfileAPIView.as_view()),





    path('dash/', dashboard, name='dashboard'), 
   path('room/<int:room_id>/', chat_room, name="chatroom"),
]
