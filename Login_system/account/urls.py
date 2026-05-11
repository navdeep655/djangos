from .views import *
from django .urls import path

urlpatterns=[path("signup/api/",signupapi.as_view(),name="signupapi"),
             path("login/api/",signinapi.as_view(),name="loginapi"),
             path("logout/api/",logoutapi.as_view(),name="logoutapi"),
             path('product/api/',productapi.as_view(), name='productapi'),
             path('profile/api/',profileapi.as_view(), name='eprofileapi'),
             path('cart/api/',cartapi.as_view(),name="cartapi"),
             path('cartlist/api/',cartlist.as_view(),name="cartlist"),
             path('cart/update/api/<int:cart_id>/', cartupdateapi.as_view(),name="cart_update"),
             path('cart/delete/api/<int:cart_id>/', cartdeleteapi.as_view(),name="cart_delete"),
             path("checkout/api/",checkoutapi.as_view(),name="checkout"),
             path("placeorder/api/",placeorderapi.as_view(),name="placeorder"),
             path("orderdetails/api/<int:order_id>/",orderdetailsapi.as_view(),name="orderdetails"
),
           
]

urlpatterns+=[path("dashboard/",dashboard,name="dashboard"),
            path("signup/",signup,name="signup"),
            path("both/",both,name="both"),
            path("login/",login,name="login"),
            path("profile/",profile,name="profile"),
            path('editprofile/',edit_profile, name='edit_profile'),
            path('product/',product,name="product"),
            path('cart/',cart,name='cart' ),
            path('checkout/',checkoutpage,name='checkout'),
            path('payment/', paymentpage, name='payment'),
            path('orderdetails/<int:order_id>/',orderdetailspage,name='orderdetailspage'),
           ]

           
            
            



