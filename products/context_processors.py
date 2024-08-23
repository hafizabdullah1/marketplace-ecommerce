from django.contrib.auth import get_user_model
from user_accounts.models import Store


CustomUser = get_user_model()

#  fetch the cart data and send it to the all template.
def cart_summary(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values())
    return {'cart_qty': total_quantity}


# To check seller store activation in anywhere in seller dashboard
def store_context(request):
    store = None
    if request.user.is_authenticated:
        user = request.user
        if user.role == 'seller': 
            try:
                store = Store.objects.get(user=user)
            except Store.DoesNotExist:
                store = None
    return {'store': store}
