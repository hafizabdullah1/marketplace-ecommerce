from django.urls import path
from .views import *

urlpatterns = [
    path("", home_products, name="home"),
    path("create_product/", create_product, name="create_product"),
    path("products_list/", products_list, name="products_list"),
    path("products_by_user/<int:user_id>/", products_by_user, name="products_by_user"),
    path("product_detail/<int:product_id>/", product_detail, name="product_detail"),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),
    path('update_product/<int:product_id>/', update_product, name='update_product'),
    
    # add to cart related urls
    path('cart_add/', cart_add, name='cart_add'),
    path('cart_items/', cart_items, name='cart_items'),
    path('delete-cart-item/', delete_cart_item, name='delete_cart_item'),
    path('update-cart-quantity/', update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', create_order, name='checkout'),
    
    # Order related urls
    path('order_summary/<int:order_id>/', order_summary, name='order_summary'),
    path('order_history/', order_history, name='order_history'),
    path('seller_orders/', seller_orders, name='seller_orders'),
    
    # stripe
    path('payment/<int:order_id>/', payment, name='payment'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    
    # analytics
    path('order_analytics/', order_analytics, name="order_analytics"),
    path('analytics/', analytics, name='analytics'),

]