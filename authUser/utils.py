from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import CustomUser



def send_verification_email(user):
    message = f"Your verification code is: {user.code}"

    send_mail(
        subject='Verification',
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )



