from django.urls import path
from .import views

urlpatterns=[
             path('home/',views.home,name="home"),
             path('about/',views.about,name="about"),
             path('contact/',views.contact,name="contact"),
             path('<int:student_id>/', views.student_detail, name="student_detail"),
             path('add/',views.form_data,name="form_data")]