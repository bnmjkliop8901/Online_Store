from rest_framework import viewsets , generics
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer, AddressCreateSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model



class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AddressCreateSerializer
        return AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
