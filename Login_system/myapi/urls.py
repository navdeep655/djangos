from .views import *
from django .urls import path
from rest_framework_simplejwt.views import(TokenObtainPairView,TokenRefreshView)

urlpatterns=[path("product/",get_products,name="products"),
            path("api/product/",post_product,name="postproduct" ),
            path("api/staff/",staff_view,name="staff"),
            path('api/login/',TokenObtainPairView.as_view()),
            path("api/refresh/",TokenRefreshView.as_view())]