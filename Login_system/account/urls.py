from .views import *
from django .urls import path

urlpatterns=[path("signup/",signup,name="signup"),
             path("login/",signin,name="login"),
             path("dashboard/",dashboard,name="dashboard"),
             path("logout/",logout_fun,name="logout"),

             path("profile/",profile,name="profile"),
             path('editprofile/',edit_profile, name='edit_profile'),
             path('product/',product_list, name='product'),
             path('add/<int:product_id>/',cart,name='addcart'),
             path('cart/',cart_page,name='cart' ),
             path('remove/<int:cart_id>/',remove_from_cart, name='remove'),
             path('update/<int:cart_id>/<str:action>/',update_cart,name='update_cart'),
             path('checkout/',checkout,name='checkout'),
             path('order-success/',order_success,name='order_success'),
             path('payment/', payment, name='payment'),
             path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),]
