from .views import *
from django.urls import path
from rest_framework_simplejwt.views import(TokenObtainPairView,TokenRefreshView)

urlpatterns=[
    path("api/refresh/",TokenRefreshView.as_view()),
    path("api/signup/",SignupApiView.as_view(),name="signup"),
    path("api/login/",LoginApi.as_view(),name="login"),
    path("api/profile/",ProfileView.as_view(),name="profile"),
    path('api/logout/',LogoutApi.as_view, name='logout'),

]

urlpatterns+=[path('signup/', signup_page, name='signup'),
path('login/',  login_page,  name='login'),
path('dashboard/', dashboard_page, name='dashboard'),
path('profile/',   profile_page,   name='profile'),]