from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('login/', login_user, name="login"),
    path('register/', register_user, name="register"),
    path('register/verify/<str:token>/', verify_email, name="verify_email"),
    path('register/verify-email-sent/', verify_email_send, name="verify_email_send"),
    path('logout/', logout_user, name="logout"),
    
    
    path('test/', test, name="test"),
    
    
]
