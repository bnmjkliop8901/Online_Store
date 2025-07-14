from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, AddressViewSet,
    RegisterView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = router.urls + [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
