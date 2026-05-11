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
    
def signup(request):
    return render(request,"account/signup.html")

def both(request):
    return render(request,"account/both.html")

def login(request):
    return render(request,"account/login.html")


@jwt_required
def dashboard(request):
    latest_order = Order.objects.filter(user=request.user).order_by("-id").first()
    return render(request,"account/dashboard.html",{"latest_order": latest_order })


@jwt_required
def profile(request):
    return render(request,"account/profile.html")

@jwt_required
def edit_profile(request):
    return render(request,"account/edit_profile.html")

@jwt_required
def product(request):
    return render(request,"account/products.html")

@jwt_required
def cart(request):
    return render(request,"account/cart.html")
@jwt_required
def checkoutpage(request):
    return render( request,"account/checkout.html")
@jwt_required
def paymentpage(request):
    return render( request,"account/payment.html")
@jwt_required
def orderdetailspage(request, order_id):
    return render( request,"account/orderdetails.html")





class profileapi(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        profile=profile_data.objects.get(user=request.user)
        serializer=profile_serializer(profile)
        return Response(serializer.data)
    def put(self,request):
        profile=profile_data.objects.get(user=request.user)
        serializer=profile_serializer(profile,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"profile_updated","data":serializer.data})

   


class productapi(APIView):
    authentication_classes = []
    # permission_classes=[]
    def get(self,request):
        products = Product.objects.all()
        serial=product_serializer(products,many=True)
        return Response({"data": serial.data})
   

class cartapi(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,request):
        user=request.user
        product_id = request.data.get("product")
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        cart_item, created = Cart.objects.get_or_create(user=user,product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += int(quantity)
        cart_item.save()
        return Response({"message":"Product added to cart","quantity": cart_item.quantity})
    


class cartlist(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        cart = Cart.objects.filter(user=request.user)
        serializer = cart_serializer(cart, many=True)
        total = sum(item.total_price() for item in cart)
        return Response({"cart": serializer.data,"total": total})
    




class cartupdateapi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    parser_classes = [JSONParser]
    def post(self, request, cart_id):
        action = request.data.get('action') 
        print(request.data)
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        if action == "inc":
            cart_item.quantity += 1
        elif action == "dec":
            cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            
            return Response({"message": "Item removed"})

        cart_item.save()
        return Response({
            "message": "Updated",
            "quantity": cart_item.quantity
        })
  

class cartdeleteapi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def delete(self, request, cart_id):
        Cart.objects.filter(id=cart_id, user=request.user).delete()

        return Response({"message": "Deleted successfully"})


class checkoutapi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    def get(self, request):
        profile = profile_data.objects.get(user=request.user)
        full_name = (profile.user.first_name + " " + profile.user.last_name)
        return Response({ "name": full_name, "email": profile.user.email,"phone": profile.phone,"address": profile.address})
    def post(self, request):
        serializer = ShippingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message":"Address Saved"})
        return Response(serializer.errors)
    


class placeorderapi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        user = request.user
        # GET CART ITEMS
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({
                "error": "Cart is Empty"
            })
        # GET LATEST SHIPPING
        shipping = ShippingAddress.objects.filter(user=user).order_by("-id").first()
        if not shipping:
            return Response({"error": "Please add shipping address first"})

        # CALCULATE TOTAL
        total = 0
        for item in cart_items:
            total += (item.product.price *item.quantity)

        # CREATE ORDER
        order_data = {
            "user": user.id,
            "shipping_address": shipping.id,
            "total_amount": total,
            "payment_status": False,
            "order_status": "Pending"}

        order_serializer = OrderSerializer(data=order_data )

        if order_serializer.is_valid():
            order = order_serializer.save()
        else:
            return Response(order_serializer.errors)
        # CREATE ORDER ITEMS
        for item in cart_items:
            item_data = {
                "order": order.id,
                "product": item.product.id,
                "quantity": item.quantity,
                "price": item.product.price
            }
            item_serializer = OrderItemSerializer(data=item_data)
            if item_serializer.is_valid():
                item_serializer.save()
            else:
                return Response(item_serializer.errors)
        # CLEAR CART
        cart_items.delete()
        return Response({ "message": "Order Placed Successfully ","order_id": order.id, "total_amount":total })

class orderdetailsapi(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    def get(self, request, order_id):
        user = request.user
        order = Order.objects.get( id=order_id, user=user)
        items = OrderItem.objects.filter(order=order)
        product_data = []
        for item in items:
            product_data.append({"product_name":item.product.name,"product_image":item.product.image.url,"price": item.price, "quantity":item.quantity,"subtotal":item.price * item.quantity})

        return Response({
            "order_id": order.id,
            "total_amount":order.total_amount,
            "order_status":order.order_status,
            "payment_status":order.payment_status,
            "shipping_address": {"full_name": order.shipping_address.full_name,
                                    "phone":order.shipping_address.phone,
                                     "address":order.shipping_address.address,
                                     "city": order.shipping_address.city,
                                    "district": order.shipping_address.district,
                                    "state": order.shipping_address.state
            },
            "products":product_data
        })


