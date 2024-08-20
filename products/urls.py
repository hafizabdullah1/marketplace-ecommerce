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
]