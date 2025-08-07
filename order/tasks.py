from celery import shared_task
from django.core.mail import send_mail
from decouple import config
import logging
import traceback


logger = logging.getLogger(__name__)


DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

@shared_task(bind=True, max_retries=3)
def send_order_received_email(self, user_email, order_id):
    subject = "We've received your order"
    message = f"Thanks! Your order #{order_id} has been received and is being processed."
    try:
        send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email])
        logger.info(f"Order confirmation sent to {user_email}")
    except Exception as exc:
        logger.error("Email send error (order received): %s", traceback.format_exc())
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_payment_confirmed_email(self, user_email, order_id):
    subject = "Payment confirmed"
    message = f"Your payment for order #{order_id} has been successfully processed. We’ll ship it soon!"
    try:
        send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email])
        logger.info(f"Payment confirmation sent to {user_email}")
    except Exception as exc:
        logger.error("Email send error (payment confirmed): %s", traceback.format_exc())
        raise self.retry(exc=exc, countdown=60)
