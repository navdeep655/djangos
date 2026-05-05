from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class profile_data(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=10)
    address=models.CharField(max_length=100)

    def __str__(self):
        return self.User.username
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price= models.IntegerField()
    image= models.ImageField(upload_to='images/',blank=True, null=True)
    stock= models.IntegerField(default=10)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def total_price(self):
        return self.quantity*self.product.price
    


class Order(models.Model):

    STATUS = [
        ('Pending',    'Pending'),
        ('Processing', 'Processing'),
        ('Shipped',    'Shipped'),
        ('Delivered',  'Delivered'),
        ('Cancelled',  'Cancelled'),
    ]

    user  = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name   = models.CharField(max_length=100)
    address     = models.TextField()
    city        = models.CharField(max_length=50)
    state       = models.CharField(max_length=50)
    country     = models.CharField(max_length=50)
    pincode     = models.CharField(max_length=10)
    phone       = models.CharField(max_length=15)

   
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=20, choices=STATUS,  default='Pending')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price    = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.order} - {self.product.name}"









