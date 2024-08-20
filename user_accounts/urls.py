from django.urls import path
from .views import *

urlpatterns = [
    # path('', home, name="home"),
    path('login/', login_user, name="login"),
    path('register/', register_user, name="register"),
    path('register/verify/<str:token>/', verify_email, name="verify_email"),
    path('register/verify-email-sent/', verify_email_send, name="verify_email_send"),
    path('logout/', logout_user, name="logout"),    
    path('edit_user/<int:user_id>/', edit_user, name="edit_user"),    
    path('seller_store_info/', seller_store_info, name="seller_store_info"),
    
    # Seller dashboard related views
    path('seller_dashboard/', seller_dashboard, name='seller_dashboard'),
    path('store_info/<int:user_id>', store_info, name='store_info'),
    path('store/update/<int:store_id>/', update_store, name='update_store'),

    
    
    # Admin accessed routes
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
]