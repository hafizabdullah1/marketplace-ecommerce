from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from marketplace.decorators import *
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth


# all products list to sellers and buyers
def home_products(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    if request.user.is_authenticated and request.user.is_banned: 
        return render(request, 'account_blocked.html')

    products = Product.objects.all()
    context = {'products': products}
    return render(request, "products/products.html", context)

@role_required('admin')
def products_list(request):
    products = Product.objects.all()
    
    context = {'products': products}
    return render(request, "products/products_list.html", context)


# Single seller products
def products_by_user(request, user_id):
    if request.user.is_authenticated and request.user.role == 'buyer':
        return redirect('home')
    
    user = None
    try:   
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found")
        print("Error while get user in products by user")
        
    print("check user", user.id == request.user.id)

    products = Product.objects.filter(author = user)
    context = {'products': products, "user": user}
    return render(request, "products/products_by_user.html", context)


# view single product
def product_detail(request, product_id):
    product = None
    try:   
        product = Product.objects.get(id=product_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Product not found")
        print("Error while get product in products detail")
        
    context = {'product': product}
    return render(request, 'products/product_detail.html', context)


# create product
def create_product(request):
    if request.user.is_authenticated and request.user.role == 'buyer':
        return redirect('home')

    if request.method == 'POST':
        author = request.user
        # category_id = request.POST.get("category")
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        brand = request.POST.get("brand")
        color = request.POST.get("color")
        price = request.POST.get("price")
        countInStock = request.POST.get("countInStock")
        
        # category = None
        
        # try:
        #     category = Categorie.objects.get(id=category_id)
        # except Categorie.DoesNotExist:
        #     messages.error(request, "Category not found")
        
        Product.objects.create(
            author          = author,
            # category        = category,
            title           = title,
            description     = description,
            image           = image,
            brand           = brand,
            color           = color,
            price           = price,
            countInStock    = countInStock
        )
        
        messages.success(request, 'Product created successfully.')
        return redirect('products_by_user', user_id=request.user.id)

    # categories = Categorie.objects.filter(author = request.user)
    # context = {'categories': categories}
    return render(request, "products/create_product.html")



# delete product
def delete_product(request, product_id):
    if request.user.is_authenticated and request.user.role == 'buyer':
        return redirect("home")
    
    if request.method == 'DELETE':
        product = get_object_or_404(Product, id=product_id)
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully.')
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Failed to delete product: {str(e)}')
            return JsonResponse({'success': False})
    else:
        messages.error(request, 'Invalid request method.')
        return JsonResponse({'success': False})



# Update product
def update_product(request, product_id):
    if request.user.is_authenticated and request.user.role == 'buyer':
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Update product details
        # category_id = request.POST.get('category')
        title = request.POST.get('title')
        description = request.POST.get('description')
        brand = request.POST.get('brand')
        color = request.POST.get('color')
        price = request.POST.get('price')
        count_in_stock = request.POST.get('countInStock')
        image = request.FILES.get('image')
        is_active = 'is_active' in request.POST  # Checkbox presence check
        
        # Validate required fields
        if not all([title, description, brand, color, price, count_in_stock]):
            messages.error(request, 'All fields except image are required.')
        else:
            # Update the product instance
            # product.category_id = category_id
            product.title = title
            product.description = description
            product.brand = brand
            product.color = color
            product.price = price
            product.countInStock = count_in_stock

            if is_active:
                product.is_active = is_active

            if image:
                product.image = image
            product.save()
            
            messages.success(request, 'Product updated successfully.')
            return redirect('products_by_user', user_id=request.user.id)
    
    # categories = Categorie.objects.filter(author = product.author)
    # context = {'categories': categories, 'product': product }
    context = {'product': product }
    return render(request, 'products/update_product.html', context)


# add to cart product
def cart_add(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')

    if request.method == 'POST':
        product_id = request.POST.get("productId")
        quantity = int(request.POST.get("quantity"))
        
        # fetch cart 
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
            
        # save cart 
        request.session['cart'] = cart
        request.session.modified = True
        
        # Get the total quantity of items in the cart
        cart_qty = sum(cart.values())
        
        messages.success(request, 'Product added successfully.')
        return JsonResponse({'success': True, 'cart_qty': cart_qty})

    messages.error(request, 'Server could not understand the request.')
    return JsonResponse({'success': False}, status=400)


# display cart
def cart_items(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')

    cart = request.session.get('cart', {})
    product_ids = cart.keys()

    products = Product.objects.filter(id__in=product_ids)

    cart_products = []
    subtotal = 0

    for product in products:
        quantity = cart.get(str(product.id), 0)
        total_price = product.price * quantity
        subtotal += total_price

        cart_products.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
        })

    context = {
        'cart_products': cart_products,
        'subtotal': subtotal,
        'total': subtotal + 199
    }
    return render(request, "products/cart_items.html", context)


# update cart
def update_cart_quantity(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        
        cart = request.session.get('cart', {})
        
        if quantity > 0:
            if product_id in cart:
                cart[product_id] = quantity
                request.session['cart'] = cart
                return JsonResponse({'status': 'success', 'message': 'Quantity updated successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



# delete cart item
@require_POST
def delete_cart_item(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    product_id = request.POST.get('product_id')
    cart = request.session.get('cart', {})

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Item not found in cart'})



# checkout
def create_order(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login to checkout.")
        return redirect("login")
    
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        cart = request.session.get('cart', {})

        if not address or not city or not cart:
            messages.error(request, "Please fill out all required fields.")
            return redirect('checkout')  

        total_amount = 0

        try:
            order = Order.objects.create(
                user=request.user,
                address=address,
                city=city,
                ordered_at=timezone.now()
            )
        except Exception as e:
            messages.error(request, f"Failed to create order: {e}")
            return redirect('checkout')

        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                quantity = int(quantity)
                price = product.price * quantity
                total_amount += price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
            except Product.DoesNotExist:
                messages.error(request, f"Product with ID {product_id} does not exist.")
                return redirect('checkout')
            except Exception as e:
                messages.error(request, f"Failed to create order item: {e}")
                return redirect('checkout')

        order.total_amount = total_amount
        order.save()

        request.session['cart'] = {}

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_summary', order_id=order.id)

    return render(request, 'products/checkout.html')


# order summary 
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'products/order_summary.html', context)


# Stripe payment
stripe.api_key = settings.STRIPE_SECRET_KEY
def payment(request, order_id):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        if not token:
            messages.error(request, "Payment failed. Please try again.")
            return redirect('payment', order_id=order_id)
        try:
            charge = stripe.Charge.create(
                amount=int(order.total_amount * 100),  # Amount in cents
                currency='usd',
                description=f'Order {order_id}',
                source=token,
            )

            order.is_paid = True
            order.save()

            order_items = OrderItem.objects.filter(order=order)

            for item in order_items:
                product = item.product
                product.countInStock -= item.quantity
                product.save()

            messages.success(request, "Payment successful! Thank you for your order.")
            return redirect('home')
        except stripe.error.CardError as e:
            messages.error(request, f"Payment failed: {e.user_message}")
            return redirect('payment', order_id=order_id)
    
    # Render the payment page
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'order': order
    }
    return render(request, 'products/payment.html', context)


# web hook for stripe events
@csrf_exempt
def stripe_webhook(request):
    print("Webhook called")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    # print(f"Payload: {payload}")
    print(f"Signature Header: {sig_header}")

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print(f"Constructed Event: {event}")
    except ValueError as e:
        print(f"Invalid Payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Signature Verification Error: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment for {payment_intent['amount']} succeeded.")
        order_id = payment_intent.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()
                print(f"Order {order_id} marked as paid.")
            except Order.DoesNotExist:
                print(f"Order {order_id} does not exist.")
                pass

    return HttpResponse(status=200)



# user orders history
def order_history(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    orders = Order.objects.filter(user=request.user)
    context = {'orders': orders }
    return render(request, "products/order_history.html", context)

# seller orders
@role_required('seller')
def seller_orders(request):
    
    # orders = Order.objects.filter(orderitem__product__author=request.user).distinct()
    # Find orders containing products authored by the current seller
    order_ids = OrderItem.objects.filter(
            product__author=request.user
        ).values_list('order_id', flat=True).distinct()
        
        # Filter orders by these IDs
    orders = Order.objects.filter(id__in=order_ids)

    context = {'orders': orders}
    return render(request, "products/seller_orders.html", context)


# Orders analytics
@login_required
def order_analytics(request):
    if request.user.role == 'buyer':
        return redirect('home')
        
    user = request.user
    
    if user.role == 'seller':
        # Find orders containing products authored by the current seller
        order_ids = OrderItem.objects.filter(
            product__author=user
        ).values_list('order_id', flat=True).distinct()
        
        # Filter orders by these IDs
        orders = Order.objects.filter(id__in=order_ids)

        # Calculate total sales for products authored by the seller
        total_sales = OrderItem.objects.filter(
            order__in=orders,
            product__author=user
        ).aggregate(total_sales=Sum('price'))['total_sales'] or 0
        
        # Monthly sales aggregation for the seller's products
        monthly_data = OrderItem.objects.filter(
            order__in=orders,
            product__author=user
        ).annotate(
            month=TruncMonth('order__ordered_at')
        ).values('month').annotate(
            total_sales=Sum('price'),
            order_count=Count('order_id')
        ).order_by('month')

    else:
        # Admin sees all orders
        orders = Order.objects.all()
        
        # Calculate total sales for all orders
        total_sales = orders.aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0
        
        # Monthly sales aggregation for all orders
        monthly_data = orders.annotate(
            month=TruncMonth('ordered_at')
        ).values('month').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('month')

    months = [entry['month'].strftime('%Y-%m') for entry in monthly_data]
    sales = [entry['total_sales'] for entry in monthly_data]
    orders_count = [entry['order_count'] for entry in monthly_data]

    data = {
        'total_sales': total_sales,
        'order_count': orders.count(),  # Count of all orders
        'months': months,
        'sales': sales,
        'orders': orders_count
    }
    return JsonResponse(data)


# analytics template rendering
def analytics(request):
    return render(request, "products/analytics.html")