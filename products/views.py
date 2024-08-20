from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

# Create your views here.

# all products list to show to admin

def home_products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, "products/products.html", context)


def products_list(request):
    products = Product.objects.all()
    
    context = {'products': products}
    return render(request, "products/products_list.html", context)


# Single seller products
def products_by_user(request, user_id):
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
    if request.user.role == 'buyer':
        return redirect('home')

    if request.method == 'POST':
        author = request.user
        category_id = request.POST.get("category")
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        brand = request.POST.get("brand")
        color = request.POST.get("color")
        price = request.POST.get("price")
        countInStock = request.POST.get("countInStock")
        
        category = None
        
        try:
            category = Categorie.objects.get(id=category_id)
        except Categorie.DoesNotExist:
            messages.error(request, "Category not found")
        
        Product.objects.create(
            author          = author,
            category        = category,
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

    categories = Categorie.objects.filter(author = request.user)
    context = {'categories': categories}
    return render(request, "products/create_product.html", context)



# delete product
def delete_product(request, product_id):
    if request.user.role == 'buyer':
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
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Update product details
        category_id = request.POST.get('category')
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
            product.category_id = category_id
            product.title = title
            product.description = description
            product.brand = brand
            product.color = color
            product.price = price
            product.countInStock = count_in_stock
            product.is_active = is_active
            if image:
                product.image = image
            product.save()
            
            messages.success(request, 'Product updated successfully.')
            return redirect('products_by_user', user_id=request.user.id)
    
    categories = Categorie.objects.filter(author = product.author)
    context = {'categories': categories, 'product': product }
    return render(request, 'products/update_product.html', context)



# add to cart product
def cart_add(request):
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
from django.http import JsonResponse

def update_cart_quantity(request):
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
    product_id = request.POST.get('product_id')
    cart = request.session.get('cart', {})

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Item not found in cart'})
