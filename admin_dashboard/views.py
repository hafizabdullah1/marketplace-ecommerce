from django.shortcuts import render, get_object_or_404
from user_accounts.models import *
from marketplace.decorators import role_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import *
from django.db.models import Count, OuterRef, Subquery

# Create your views here.

# Admin dashboard
@role_required("admin")
def dashboard(request):
    path = request.path
    pending_req = len(Store.objects.filter(status = False))
    total_sellers = len(CustomUser.objects.filter(role = 'seller'))
    total_orders = len(Order.objects.all())
    pending_orders = len(Order.objects.filter(status=False))
    
    context = {'path': path, 'total_sellers': total_sellers, 'pending_req': pending_req, 'total_orders': total_orders, 'pending_orders': pending_orders}
    return render(request, "admin_dashboard/dashboard.html", context)


# Lists all users
@role_required("admin")
def manage_users(request):
    users = CustomUser.objects.all()
    path = request.path
    context = {'users': users, 'path': path}
    return render(request, "admin_dashboard/manage_users.html", context)


# Seller accounts requeusts
@role_required("admin")
def seller_requests(request):
    pending_req = Store.objects.filter(status = False)
    path = request.path
    context = {'pending_req': pending_req,'path': path}
    return render(request, "admin_dashboard/seller_accounts_req.html", context)


# Approved seller account 
@require_POST
@role_required("admin")
def approved_store(request):
    store_id = request.POST.get('store_id')
    try:
        store = Store.objects.get(id=store_id)
        store.status = True
        store.save()
        return JsonResponse({'success': True, 'message': 'Store approved successfully'})
    
    except Store.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Store not found'})

# list of all stores
@role_required("admin")
def store_lists(request):
    path = request.path
     # Subquery to count products for each store's user
    product_count_subquery = Product.objects.filter(
        author=OuterRef('user')  # Assuming 'author' in Product is the ForeignKey to User
    ).values('author').annotate(
        total_products=Count('id')
    ).values('total_products')
    
    # Annotate each store with the total number of products for the store's user
    stores = Store.objects.annotate(
        total_products=Subquery(product_count_subquery)
    )
    
    context = {'stores': stores, 'path': path}
    return render(request, "admin_dashboard/store_lists.html", context)
    

# Toggle store status
@role_required('admin')
@require_POST
def toggle_store_status(request):
    store_id = request.POST.get('store_id')
    is_active = request.POST.get('is_active') == 'true'

    try:
        store = Store.objects.get(id=store_id)
        store.is_active = is_active
        store.save()
        messages.success(request, 'Store status updated successfully')
        return JsonResponse({'success': True, 'message': 'Store status updated successfully'})
    except Store.DoesNotExist:
        messages.error(request, 'Store not found')
        return JsonResponse({'success': False, 'message': 'Store not found'})


# View store
@role_required('admin')
def view_store(request, store_id):
    store = None
    try:
        store = Store.objects.get(id = store_id)
        
        total_products = len(Product.objects.filter(author = store.user))
    except Store.DoesNotExist:
        messages.error(request, "Store not found")
        print("Error while view store")

    path = request.path
    context = {'path': path, 'store': store, 'total_products': total_products}
    return render(request, "admin_dashboard/view_store.html", context)

# All orders
@role_required('admin')
def all_orders(request):
    orders = Order.objects.all()
    context = {'orders': orders }
    return render(request, "admin_dashboard/all_orders.html", context)
    
    
# Delete orders
def delete_order(request):
    if request.user.is_authenticated and request.user.role == 'buyer':
        return render(request, "user_dashboard")
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        messages.success(request, 'Order successfully deleted.')
        return JsonResponse({'success': True, 'message': 'Order successfully deleted.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

    
# Mark delivered to order
def mark_as_delivered(request):
    if request.user.is_authenticated and request.user.role == 'buyer':
        return render(request, "user_dashboard")
 
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        order.status = True
        order.is_paid = True
        order.save()
        messages.success(request, 'Order marked as delivered and payment status updated.')
        return JsonResponse({'success': True, 'message': 'Order marked as delivered and payment status updated.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})
