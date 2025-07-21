import random
import os
import traceback
from django.core.cache import cache
from django.core.mail import send_mail
from kavenegar import KavenegarAPI
from decouple import config

# 🔐 Environment variables
KAVENEGAR_API_KEY = config("KAVENEGAR_API_KEY")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")


# 🔢 OTP generator
def generate_otp():
    return str(random.randint(100000, 999999))


# 🚀 Send OTP and cache it
def send_otp(user):
    otp = generate_otp()
    cache.set(f"otp_{user.username}", otp, timeout=300)
    print(f"OTP for {user.username}: {otp}")
    return otp


# ✅ Verify OTP
def verify_otp(user, input_otp):
    stored_otp = cache.get(f"otp_{user.username}")
    return stored_otp == input_otp


# 📧 Send OTP via email
def send_otp_email(email, otp):
    subject = 'Your Login OTP'
    message = f'Hi! Your one-time login code is: {otp}'
    send_mail(subject, message, EMAIL_HOST_USER, [email])
    print(f"OTP sent via email to {email}")


# 📱 Send OTP via SMS using Kavenegar
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
        print("SMS sent:", response)
        return response
    except Exception as e:
        print("SMS Error:\n", traceback.format_exc())
        return None


# 🔁 Combined fallback logic: SMS first, email if SMS fails
def send_otp_with_fallback(user):
    otp = generate_otp()
    cache.set(f"otp_{user.username}", otp, timeout=300)
    print(f"Generated OTP for {user.username}: {otp}")

    sms_response = send_otp_sms(user.phone, otp)

    if sms_response is None:
        print(f"SMS failed for {user.phone}. Fallback to email: {user.email}")
        send_otp_email(user.email, otp)
