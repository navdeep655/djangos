from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Student
from .form import StudentForm


# Create your views here.
def home(request):

    data_list = [
        {'name': 'Arjun',   'age': 20},
        {'name': 'Priya',   'age': 21},
    ]
    
    context={'page_title':'Home',
             "lists":data_list,
            'total_people': 4,
            'app_name': 'Management System'
    }
    #return HttpResponse("<h1>Welcome to app1</h1>")
    return render(request,"app1/home.html",context)

def about(request):
    list1={"name":"Navdeep"}
    content={"owner":list1}
    return render(request,"app1/about.html",content)
    #return HttpResponse("<h1>Wlecome to about page</h1>")

def contact(request):
    student=Student.objects.all()
    data={"sdata":student}
    return render(request,"app1/contact.html",data)
    return HttpResponse("<h1>Welcome to the contact page</h1>")

def student_detail(request,student_id):
    return HttpResponse(f"<h1> Enter student id for detail {student_id}</h1>")




def form_data(request):
    if request.method=="POST":
        form=StudentForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            age=form.cleaned_data["age"]
            email=form.cleaned_data["email"]
            address=form.cleaned_data["address"]
        Student.objects.create(name=name,age=age,email=email,address=address)
        return redirect("form_data")
    else:
        form=StudentForm()
    return render(request,"app1/data.html",{"form":form})

    

