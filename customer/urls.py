from django.urls import path
from rest_framework.routers import DefaultRouter
from customer.views import (
    CustomerViewSet, AddressViewSet, RegisterView,
    RequestOTPView, VerifyOTPView, MeView,
    AdminCustomerViewSet, AdminAddressViewSet , LogoutView
)
from rest_framework_simplejwt.views import TokenRefreshView



router = DefaultRouter()
# router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'addresses', AddressViewSet, basename='address')


admin_router = DefaultRouter()
admin_router.register(r'admin-customers', AdminCustomerViewSet, basename='admin-customer')
admin_router.register(r'admin-addresses', AdminAddressViewSet, basename='admin-address')

urlpatterns = router.urls + admin_router.urls + [
    # path('register/', RegisterView.as_view(), name='register'),
    path('auth/register/', RegisterView.as_view(), name='register'), 
    path("auth/logout/", LogoutView.as_view(), name="logout"),  
    # path('otp/request/', RequestOTPView.as_view(), name='request_otp'),
    path('accounts/request-otp/', RequestOTPView.as_view(), name='request_otp'),    
    # path('otp/verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('accounts/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    # path('me/', MeView.as_view(), name='user-profile'),
    path('myuser/', MeView.as_view(), name='user-profile'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
