from .views import *
from django.urls import path
from rest_framework_simplejwt.views import(TokenObtainPairView,TokenRefreshView)

urlpatterns=[path("api/signup/",signup,name="signup"),
            path("api/refresh/",TokenRefreshView.as_view()),
            path("api/login1/",djlogin,name="login"),
            path("signup/", signup_page,name="signup1"),
            path("login/",login_page,name="login1"),
            path("dashboard/",dashboard,name="dashboard"),
            path('api/logout/',djlogout, name='logout'),
            
            path("api/product/",get_products,name="product")]


urlpatterns+=[
    path("api/update/<int:product_id>/",update,name="update"),
    path("api/patch/<int:product_id>/",update_any,name="patch"),
    path("api/delete/<int:product_id>/",delete,name="delete"),
    path('product/<int:pk>/', Productview.as_view()),
    path('pro/<int:pk>/', ProductDetailAPIView.as_view()),
    path('pro/', ProductDetailAPIView.as_view()),
    #genric
    path('prot', ProductView.as_view())
]

from rest_framework.routers import DefaultRouter
router=DefaultRouter()
router.register("products",productviewset,basename="Product")
router.register("search",searchfilter,basename="search")

urlpatterns += router.urls

