from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
from .utils import *
import uuid
from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required      
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from marketplace.decorators import role_required
from products.models import *
          

# Create your views here.

def home(request):
    store = None
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    if request.user.is_authenticated:
        if request.user.role == 'seller':
            store = Store.objects.get(user = request.user)
            
            print("store: ", store.status)
        print("out store: ", store)
    return render(request, "home.html", {'store': store})


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
            
            login(request, user)
            
            if user.role == 'seller':
                messages.success(request, "Email verified successfully. Please submit your store information.")
                return redirect('seller_store_info')
            else:
                messages.success(request, "Email verified successfully.")
                return redirect('login')
        else:
            messages.error(request, "Invalid token.")
    except CustomUser.DoesNotExist:
        return render(request, 'user_accounts/email_verification_failed.html')

    return render(request, 'user_accounts/email_verification_success.html')
    
# When email was send
def verify_email_send(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "user_accounts/verify_email_send.html")
    
# Logout user
@login_required(login_url='/login')
def logout_user(request):
    logout(request)
    return redirect('login')


# Delete user
@role_required('admin')
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = CustomUser.objects.get(pk=user_id)
            user.delete()
            messages.success(request, 'User deleted successfully!')
            return JsonResponse({'success': True})
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)


# Edit user
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        is_banned = request.POST.get('is_banned') == 'on'

        user.name = name
        user.email = email
        user.role = role
        user.is_banned = is_banned
        user.save()

        messages.success(request, 'User updated successfully.')
        return redirect('users')

    return render(request, 'user_accounts/update_user.html', {'user': user})


# create seller store
# @login_required
def seller_store_info(request):
    if request.user.role != 'seller':
        return redirect('home')
    
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        title = request.POST.get('title')
        image = request.FILES.get('image')
        
        Store.objects.create(
            user=request.user,
            bussines_name=business_name,
            title=title,
            image=image
        )
        messages.success(request, 'Store information submitted successfully.')
        return redirect('home')
    
    return render(request, 'user_accounts/seller_store_info.html')


# seller dashboard
def seller_dashboard(request):
    
    user = request.user
    path = request.path
    
    store = Store.objects.get(user = user)
    
    total_products = len(Product.objects.filter(author = user))
    
    # context = {}
    context = {'store': store, 'path': path, 'total_products': total_products}
    return render(request, "user_accounts/seller_dashboard.html", context)


# View Store Detail
def store_info(request, user_id):
    store = None
    try:
        store = Store.objects.get(user = user_id)
    except Store.DoesNotExist:
        messages.error(request, "Store not found")
        
    context = {'store': store}
    return render(request, "user_accounts/store_info.html", context)


# Edit Store info
def update_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        bussines_name = request.POST.get('bussines_name')
        title = request.POST.get('title')
        image = request.FILES.get('image')

        store.bussines_name = bussines_name
        store.title = title
        if image:
            store.image = image
        store.save()

        messages.success(request, 'Store updated successfully!')
        return redirect('store_info', user_id=store.user.id)
    else:
        return render(request, 'user_accounts/update_store.html', {'store': store})

        
# User dashboard
role_required('buyer')
def user_dashboard(request):
    context = {}
    return render(request, "user_accounts/user_dashboard", context)