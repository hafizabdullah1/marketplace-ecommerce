from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
from .utils import *
import uuid
from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required                

# Create your views here.

def home(request):
    if request.user.is_superuser:
        return redirect("test")
    return render(request, "home.html")

def test(request):
   
    return render(request, "test.html")


# Login user
def login_user(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if not CustomUser.objects.filter(email = email).exists():
            messages.error(request, "Invalid email")
            return redirect("login")
        
        checkUser = CustomUser.objects.filter(email = email)
        print("password:", checkUser[0].password)
        print("email:", checkUser[0].email)
        
        user = authenticate(username = email, password = password)
    
        if user is None:
            print("user is none")
            messages.error(request, "Invalid password")
            return redirect('login')
        
        login(request, user)
        return redirect('home')
            
    context = {}
    return render(request, "user_accounts/login.html", context)


# Register new user
def register_user(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email').lower()
        role = request.POST.get('role')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.filter(email=email)
            if user.exists():
                messages.error(request, "Email already exixts.")
                return redirect("register")
            else:
                user = CustomUser.objects.create(
                    email = email,
                    name = name,
                    role = role,
                    email_token = str(uuid.uuid4())
                )

                user.set_password(password)
                user.save()
                send_email_token(request, email, user.email_token)
                return redirect("verify_email_send")

        except ObjectDoesNotExist:
            messages.error(request, "Error when try to find user.")
        
    context = {}
    return render(request, "user_accounts/register.html", context)


# Email verification route
def verify_email(request, token):
    try:
        user = CustomUser.objects.get(email_token=token)
        if user:
            user.is_verified = True
            user.email_token = ''
            user.save()

    except CustomUser.DoesNotExist:
        return render(request, 'user_accounts/email_verification_failed.html')

    return render(request, 'user_accounts/email_verification_success.html')
    
    
def verify_email_send(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "user_accounts/verify_email_send.html")
    
@login_required(login_url='/login')
def logout_user(request):
    logout(request)
    return redirect('login')
