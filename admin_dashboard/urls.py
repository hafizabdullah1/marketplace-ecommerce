from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name="admin_dashboard"),
    path('users/', manage_users, name="users"),
    path('seller_requests/', seller_requests, name="seller_requests"),
    path('approved_store/', approved_store, name="approved_store"),
    path('store_lists/', store_lists, name="store_lists"),
    path('toggle_store_status/', toggle_store_status, name='toggle_store_status'),
    path('view_store/<int:store_id>', view_store, name='view_store'),
]