from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class profile_data(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.ImageField(null=True, blank=True)
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
    


class ShippingAddress(models.Model):
    user = models.ForeignKey( User,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=200,blank=True,null=True)
    address = models.TextField()
   
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):

        return self.full_name
    



class Order(models.Model):

    user = models.ForeignKey( User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress,on_delete=models.CASCADE)
    total_amount = models.DecimalField( max_digits=10,decimal_places=2)
    payment_status = models.BooleanField(default=False)
    order_status = models.CharField(max_length=50,default="Pending")
    created_at = models.DateTimeField( auto_now_add=True)


class OrderItem(models.Model):

    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)










