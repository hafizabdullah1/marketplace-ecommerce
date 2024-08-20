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