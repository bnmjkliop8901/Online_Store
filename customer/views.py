from rest_framework import viewsets
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer, AddressCreateSerializer
from rest_framework.permissions import IsAuthenticated

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
