from django.contrib import admin
from.models import Student
# app1/admin.py

from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):

    # Columns shown in the list view
    list_display = ['id', 'name', 'age', 'email', 'address']
    ordering     = ['-id']  
    list_editable = ['address']   

    # Add search bar
    search_fields = ['name', 'email']

    # Add filter sidebar
    list_filter = ['address']

    # How many records per page
    list_per_page = 10

    # Make id column clickable
    list_display_links = ['id', 'name']

# Register with customization
admin.site.register(Student, StudentAdmin)

# Register your models here.
