from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = router.urls
