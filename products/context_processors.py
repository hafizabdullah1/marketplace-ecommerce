#  fetch the cart data and send it to the all template.

def cart_summary(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values())
    return {'cart_qty': total_quantity}
