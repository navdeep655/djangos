from django.shortcuts import render,redirect
from .form import *
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def signup_view(request):
    if request.method =="POST":
        form=SignupForm(request.POST)

        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])

            user.save()

            #login(request,user)
            return redirect("login")

    else:
        form=SignupForm()
    
    return render(request,"account/signup.html",{'form':form})

def login_view(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect("dashboard")
        else:
             return render(request,'account/login.html',{'error': 'Invalid username or password!'})
        
    return render(request, 'account/login.html')
    

@login_required(login_url='/account/login/') 
def dashboard(request):
    return render(request, 'account/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect("login")