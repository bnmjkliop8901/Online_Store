from django.urls import path
from .views import (
    CustomerViewSet,
    AddressViewSet,
    RegisterView,
    RequestOTPView,
    VerifyOTPView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = router.urls + [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/request/', RequestOTPView.as_view(), name='request_otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify_otp'),
]
