from django.db import models
from user_accounts.models import *

# Create your models here.
# Product category model
class Categorie(models.Model):
    name                    = models.CharField(max_length=50)
    image                   = models.ImageField(upload_to='category/')
    author                  = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    color                   = models.CharField(max_length=50, default='white')
    created_at              = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# product model
class Product(models.Model):
    author                  = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    category                = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    title                   = models.CharField(max_length=100)
    description             = models.TextField()
    image                   = models.ImageField(upload_to='products/')
    brand                   = models.CharField(max_length=20)
    color                   = models.CharField(max_length=200)
    price                   = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    countInStock            = models.IntegerField(default=0)
    created_at              = models.DateTimeField(auto_now_add=True)
    is_active               = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    
# Order model
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    status = models.BooleanField(default=False)
    address = models.TextField()
    city = models.CharField(max_length=128)
    ordered_at = models.DateTimeField(auto_created=True)
    delivered_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.name}"


# Relation between products and orders
class OrderItem(models.Model):
    order   = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price   = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} for Order {self.order.id}"