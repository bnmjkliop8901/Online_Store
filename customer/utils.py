import random
import os
from django.core.cache import cache
from django.core.mail import send_mail
from kavenegar import KavenegarAPI
import os

from decouple import config
KAVENEGAR_API_KEY = config("KAVENEGAR_API_KEY")
# KAVENEGAR_API_KEY = os.getenv("KAVENEGAR_API_KEY")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(user):
    otp = generate_otp()
    cache.set(f"otp_{user.username}", otp, timeout=300)
    print(f"OTP for {user.username}: {otp}")
    return otp

def verify_otp(user, input_otp):
    stored_otp = cache.get(f"otp_{user.username}")
    return stored_otp == input_otp


def send_otp_email(email, otp):
    subject = 'Your Login OTP'
    message = f'Hi! Your one-time login code is: {otp}'
    send_mail(subject, message, EMAIL_HOST_USER, [email])




# KAVENEGAR_API_KEY = os.getenv("KAVENEGAR_API_KEY")


def send_otp_sms(phone, otp):
    print("Loaded Kavenegar key:", KAVENEGAR_API_KEY)
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'sender': '2000660110',
            'receptor': phone,
            'message': f'Your login code is: {otp}'
        }
        response = api.sms_send(params)
        print("SMS sent ", response)
        return response
    except Exception as e:
        print("SMS Error ", str(e))
        return None
