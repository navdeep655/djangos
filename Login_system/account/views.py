from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.paginator import Paginator
# Create your views here.
import re
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters!"
    if not re.search(r'[A-Z]', password):
        return "Password must contain uppercase letter!"
    if not re.search(r'[a-z]', password):
        return "Password must contain lowercase letter!"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit!"
    if not re.search(r'[!@#$%^&*]', password):
        return "Password must contain special character (!@#$%^&*)!"
    return None
def signup(request):
    if request.method=="POST":
        username=request.POST.get("username")
        email=request.POST.get("email")
        password1=request.POST.get("password1")
        password2=request.POST.get("password2")
        
        error = validate_password(password1)
        if error:
            messages.error(request, error)
            return redirect("signup")

        if password1 !=password2:
            messages.error(request,"password did not match")
            return redirect("signup")
        if username==None:
            messages.error(request,"username cannot be empty")
            return redirect("signup")
        if User.objects.filter(username=username).exists():
            messages.error(request,"user already exists")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request,"email already exists")
            return redirect("signup")
        
        user=User.objects.create_user(username=username,email=email,password=password1)
        return redirect ("login")
    return render(request,"account/signup.html")

def signin(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]

        if not username or not password:
            messages.error(request,"Please enter Username and Password")
            return redirect("login")

        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)

            if user.is_superuser:
                return redirect('admin_dashboard')  
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("login")

    return render(request,"account/login.html")

@login_required(login_url='/account/login/') 
def dashboard(request):
    return render(request,"account/dashboard.html")

def logout_fun(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

@login_required(login_url='/account/login/')
def profile(request):
    return render(request,"account/profile.html")


@login_required(login_url='/account/login/')
def edit_profile(request):
    profiles, created = profile_data.objects.get_or_create(user=request.user)
    if request.method=="POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.save()

        profiles.phone = request.POST.get("phone")
        profiles.address = request.POST.get("address")
        profiles.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "account/edit_profile.html",{'profiles': profiles })


@login_required(login_url='/account/login/')
def product_list(request):
    products = Product.objects.all()
    paginator=Paginator(products,8)
    page=request.GET.get('page')
    products=paginator.get_page(page)
    return render(request, 'account/products.html', {'products': products})

@login_required(login_url='/account/login/')
def cart(request,product_id):
    if request.method=="POST":
        user=request.user
        product=Product.objects.get(id=product_id)
        quantity=request.POST.get("quantity")
        cart_item,create=Cart.objects.get_or_create(user=request.user,product=product)
      
        if not create:
            cart_item.quantity+=1
            cart_item.save()
            messages.success(request, "Item added to cart")
        else:
            messages.success(request, "Item added to cart")
        return redirect("product")
    return render(request,"account/cart_message.html")

@login_required(login_url='/account/login/')
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'account/cart.html', {'cart_items': cart_items,'total': total})

def remove_from_cart(request, cart_id):
    cart_item = Cart.objects.filter(id=cart_id).delete()
    # cart_item.delete().first()
    return redirect('cart')

def update_cart(request, cart_id, action):
    cart_item = Cart.objects.get(id=cart_id)
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


#############################################################################################################################
    
@login_required(login_url='/account/login/')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total      = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        address   = request.POST.get("address")
        city      = request.POST.get("city")
        state     = request.POST.get("state")
        country   = request.POST.get("country")
        pincode   = request.POST.get("pincode")
        phone     = request.POST.get("phone")
        if not full_name or not address or not city or not state or not country or not pincode or not phone:
             messages.error(request, "Please fill all fields!")
             return redirect('checkout')
        order = Order.objects.create( user = request.user, full_name= full_name,address = address, city = city,state = state,country= country,pincode= pincode,  phone= phone,
            total_price = total,
            status      = 'Pending'
        )
    
        # Har cart item ke liye OrderItem banao
        for item in cart_items:
            OrderItem.objects.create(
                order    = order,
                product  = item.product,
                quantity = item.quantity,
                price    = item.product.price
            )

        request.session['total'] = float(total)
        cart_items.delete()
        return redirect('payment')

    return render(request, 'account/checkout.html', {
        'cart_items': cart_items,
        'total'     : total
    })


# Success Page
@login_required(login_url='/account/login/')
def order_success(request):
    return render(request, 'account/order_success.html')


@login_required(login_url='/account/login/')
def payment(request):
    total = request.session.get('total', 0)
    if request.method=="POST":
        card_number=request.POST.get("card_number")
        expiry=request.POST.get("expiry")
        cvv=request.POST.get("cvv")

        if not card_number  or not expiry or not cvv:
            messages.error(request,"Enter the all details")
            return redirect('payment')

        if len(card_number)!=16:
            messages.error(request,"invalid card number ")
            return redirect('payment')
        
        if len(cvv)!=3:
            messages.error(request,"Invalid cvv number")
            return redirect('payment')

        messages.success(request, "Payment Successful!")
        return redirect('order_success')

    return render(request, 'account/payment.html', {'total': total})









#Dashboard admin

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

@staff_member_required
def admin_dashboard(request):

    # Today ki date
    today = timezone.now().date()

    #  Total Users
    total_users = User.objects.count()

    #  Aaj ke naye users
    new_users_today = User.objects.filter(
        date_joined__date=today   
    ).count()

    #  Total Orders
    total_orders = Order.objects.count()

    #  Total Revenue
    total_revenue = Order.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    #  Aaj ke orders
    orders_today = Order.objects.filter(
        created_at__date=today
    ).count()

    #  Best Selling Products
    best_products = OrderItem.objects.values(
        'product__name',
        'product__image'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    #  Recent Orders
    recent_orders = Order.objects.order_by('-created_at')[:10]

    # Last 7 days ke users
    last_7_days = User.objects.filter(
        date_joined__date__gte=today - timedelta(days=7)
    ).count()

    return render(request, 'account/admin_dashboard.html', {
        'total_users'    : total_users,
        'new_users_today': new_users_today,
        'total_orders'   : total_orders,
        'total_revenue'  : total_revenue,
        'orders_today'   : orders_today,
        'best_products'  : best_products,
        'recent_orders'  : recent_orders,
        'last_7_days'    : last_7_days,
    })
