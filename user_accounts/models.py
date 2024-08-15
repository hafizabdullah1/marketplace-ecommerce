from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import MyAccountManager

# Create your models here.


class CustomUser(AbstractUser):
    name                    = models.CharField(max_length=255)
    email                   = models.EmailField(max_length=255, unique=True)
    is_verified             = models.BooleanField(default=False, blank=True)
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