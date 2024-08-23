# your_app/templatetags/store_tags.py

from django import template
from user_accounts.models import Store

register = template.Library()

@register.simple_tag(takes_context=True)
def get_store_status(context):
    # Access the request object from the context
    request = context['request']
    
    # Retrieve the current user from the request
    user = request.user

    # Check if the user is authenticated and has the 'seller' role
    if user.is_authenticated and user.role == 'seller':
        try:
            # Retrieve the store associated with the user
            store = Store.objects.get(user=user)  # Adjust this as needed
            return store.is_active
        except Store.DoesNotExist:
            # Handle case where store does not exist for the user
            return False
    else:
        # Return False or None if the user is not a seller
        return False
