from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import MyAccountManager

# Create your models here.


class CustomUser(AbstractUser):
    username                = None
    name                    = models.CharField(max_length=255)
    email                   = models.EmailField(max_length=255, unique=True)
    is_verified             = models.BooleanField(default=False, blank=True)
    email_token             = models.CharField(max_length=200)
    is_banned               = models.BooleanField(default=False, blank=True)
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('buyer', 'Buyer')
    ]
    
    role                    = models.CharField(max_length=10, default='buyer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    
class Store(models.Model):
    user                    = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bussines_name           = models.CharField(max_length=255)
    title                   = models.CharField(max_length=255)
    status                  = models.BooleanField(default=False)
    requested_at            = models.DateTimeField(auto_now_add=True)
    verified_at             = models.DateTimeField(auto_now_add=True)
    image                   = models.ImageField(upload_to="store/", default="", blank=True, null=True)
    is_active               = models.BooleanField(default=True)

    def __str__(self):
        return self.bussines_name