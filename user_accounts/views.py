from django.shortcuts import render

# Create your views here.


def login_user(request):
    context = {}
    return render(request, "user_accounts/login.html", context)