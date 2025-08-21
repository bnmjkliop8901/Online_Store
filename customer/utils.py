import random
import traceback
import redis
from django.conf import settings
from django.core.mail import send_mail
from kavenegar import KavenegarAPI


redis_client = redis.StrictRedis.from_url(settings.REDIS_LOCATION, decode_responses=True)

KAVENEGAR_API_KEY = settings.KAVENEGAR_API_KEY
EMAIL_HOST_USER = settings.EMAIL_HOST_USER

def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp(user_id, otp, ttl=300):
    redis_client.setex(f"otp:{user_id}", ttl, otp)

def get_otp(user_id):
    return redis_client.get(f"otp:{user_id}")

def delete_otp(user_id):
    redis_client.delete(f"otp:{user_id}")

def send_otp(user):
    otp = generate_otp()
    store_otp(user.id, otp)
    print(f"[DEV] OTP for {user.username}: {otp}")
    return otp

def verify_otp(user, input_otp):
    stored = get_otp(user.id)
    if stored and stored == input_otp:
        delete_otp(user.id)
        return True
    return False

def send_otp_email(email, otp):
    subject = 'Your Login OTP'
    message = f'Hi! Your one-time login code is: {otp}'
    send_mail(subject, message, EMAIL_HOST_USER, [email])
    print(f"[DEV] OTP sent via email to {email}")

def send_otp_sms(phone, otp):
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'sender': '2000660110',
            'receptor': phone,
            'message': f'Your login code is: {otp}'
        }
        response = api.sms_send(params)
        print("[DEV] SMS sent:", response)
        return response
    except Exception:
        print("[DEV] SMS Error:\n", traceback.format_exc())
        return None

def send_otp_with_fallback(user):
    otp = generate_otp()
    store_otp(user.id, otp)
    print(f"[DEV] Generated OTP for {user.username}: {otp}")
    if send_otp_sms(user.phone, otp) is None:
        print(f"[DEV] SMS failed for {user.phone}. Fallback to email: {user.email}")
        send_otp_email(user.email, otp)
