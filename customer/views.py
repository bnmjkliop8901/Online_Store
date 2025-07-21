from rest_framework import viewsets, generics, status
from customer.models import Customer, Address
from customer.serializers import (
    CustomerSerializer, CustomerCreateSerializer,
    AddressSerializer, AddressCreateSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from customer.utils import send_otp_with_fallback, verify_otp
from django.core.cache import cache

User = get_user_model()


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
    queryset = User.objects.all()
    serializer_class = CustomerCreateSerializer
    permission_classes = [AllowAny]


class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response({"error": "Username is required."}, status=400)

        try:
            user = User.objects.get(username=username)
            send_otp_with_fallback(user)
            return Response({
                "message": "OTP sent via SMS or fallback email."
            }, status=200)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        otp_input = request.data.get("otp")

        if not username or not otp_input:
            return Response({"error": "Username and OTP required."}, status=400)

        try:
            user = User.objects.get(username=username)
            if verify_otp(user, otp_input):
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "OTP verified successfully.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }, status=200)
            else:
                return Response({"error": "Invalid OTP."}, status=400)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
