from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_email_token(request, email, token):
    try: 
        subject = 'Welcome to Our Educational Platform'
        html_message = render_to_string('user_accounts/email_verification.html', {'token': f"Click on the link to verify your account {request.build_absolute_uri()}verify/{token}"})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = email
        
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)
        
    except Exception as e:
        return False
    return True