from rest_framework import viewsets , generics , status
from customer.models import Customer, Address
from customer.serializers import CustomerSerializer, CustomerCreateSerializer , AddressSerializer, AddressCreateSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from customer.utils import send_otp, verify_otp , send_otp_email , send_otp_sms
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache




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
    serializer_class = CustomerCreateSerializer
    permission_classes = [AllowAny]






class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        channel = request.data.get("channel")  # email or phone

        if not username or not channel:
            return Response({"error": "Username and channel required."}, status=400)

        try:
            user = User.objects.get(username=username)
            otp = send_otp(user)

            if channel == "email" and user.email:
                send_otp_email(user.email, otp)
            elif channel == "phone" and user.phone:
                send_otp_sms(user.phone, otp)
            else:
                return Response({"error": "Invalid channel or missing contact info."}, status=400)

            return Response({"message": f"OTP sent via {channel}."}, status=200)

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
