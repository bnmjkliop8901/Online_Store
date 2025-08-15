# from django.contrib.auth import get_user_model
# from rest_framework import viewsets, generics, status, mixins
# from rest_framework.mixins import ListModelMixin , RetrieveModelMixin , DestroyModelMixin
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
# from customer.models import Customer, Address
# from customer.serializers import (
#     CustomerSerializer, CustomerCreateSerializer,
#     AddressSerializer, AddressCreateSerializer
# )
# from rest_framework_simplejwt.tokens import RefreshToken
# from customer.utils import send_otp_with_fallback, verify_otp

# import ipdb

# User = get_user_model()


# class MeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = CustomerSerializer(request.user, context={'request': request})
#         return Response(serializer.data)

#     def put(self, request): # put and patch
#         serializer = CustomerSerializer(request.user, data=request.data, context={'request': request} ,partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)

#     def delete(self, request):
#         request.user.delete()
#         return Response({"message": "Account deactivated."}, status=204)



# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = CustomerCreateSerializer
#     permission_classes = [AllowAny]



# class RequestOTPView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         if not username:
#             return Response({"error": "Username is required."}, status=400)

#         try:
#             user = User.objects.get(username=username, is_deleted=False)
#             send_otp_with_fallback(user)
#             return Response({"message": "OTP sent."}, status=200)
#         except User.DoesNotExist:
#             return Response({"error": "User not found."}, status=404)



# class VerifyOTPView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):

#         username = request.data.get("username")
#         otp_input = request.data.get("otp")

#         if not username or not otp_input:
#             return Response({"error": "Username and OTP required."}, status=400)

#         try:
#             user = User.objects.get(username=username, is_deleted=False)
#             if verify_otp(user, otp_input):
#                 refresh = RefreshToken.for_user(user)
#                 return Response({
#                     "message": "OTP verified.",
#                     "access": str(refresh.access_token),
#                     "refresh": str(refresh),
#                 }, status=200)
#             return Response({"error": "Invalid OTP."}, status=400)
#         except User.DoesNotExist:
#             return Response({"error": "User not found."}, status=404)



# class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Customer.objects.filter(is_deleted=False)
#     serializer_class = CustomerSerializer
#     permission_classes = [IsAuthenticated]



# class AddressViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Address.objects.filter(user=self.request.user, is_deleted=False)

#     def get_serializer_class(self):
#         if self.action in ['create', 'update', 'partial_update']:
#             return AddressCreateSerializer
#         return AddressSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def perform_destroy(self, instance):
#         instance.delete()



# # class AdminCustomerViewSet(
# #         DestroyModelMixin,
# #         ListModelMixin,
# #         RetrieveModelMixin,
# #         viewsets.GenericViewSet):
# #     queryset = Customer.objects.all()
# #     serializer_class = CustomerSerializer
# #     permission_classes = [IsAdminUser]
# class AdminCustomerViewSet(viewsets.ModelViewSet):
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializer
#     permission_classes = [IsAdminUser]

#     def perform_destroy(self, instance):
#         instance.delete()



# # class AdminAddressViewSet(
# #         DestroyModelMixin,
# #         ListModelMixin,
# #         RetrieveModelMixin,
# #         viewsets.GenericViewSet):
# #     queryset = Address.objects.all()
# #     serializer_class = AddressSerializer
# #     permission_classes = [IsAdminUser]
# class AdminAddressViewSet(viewsets.ModelViewSet):
#     queryset = Address.objects.all()
#     serializer_class = AddressSerializer
#     permission_classes = [IsAdminUser]

#     def perform_destroy(self, instance):
#         instance.delete()


from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from customer.models import Customer, Address
from customer.serializers import (
    CustomerSerializer, CustomerCreateSerializer,
    AddressSerializer, AddressCreateSerializer
)
from customer.utils import send_otp_with_fallback, verify_otp

User = get_user_model()


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomerSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        serializer = CustomerSerializer(request.user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deactivated."}, status=204)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomerCreateSerializer
    permission_classes = [AllowAny]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=205)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"error": "Username is required."}, status=400)

        try:
            user = User.objects.get(username=username, is_deleted=False)
            send_otp_with_fallback(user)
            return Response({"message": "OTP sent."}, status=200)
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
            user = User.objects.get(username=username, is_deleted=False)
            if verify_otp(user, otp_input):
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "OTP verified.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }, status=200)
            return Response({"error": "Invalid OTP."}, status=400)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.filter(is_deleted=False).order_by("id")  # Added order_by
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False).order_by("id")  # Added order_by

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AddressCreateSerializer
        return AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()


class AdminCustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_deleted=False).order_by("id")
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):
        instance.hard_delete(self.request.user)



class AdminAddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.filter(is_deleted=False).order_by("id")
    serializer_class = AddressSerializer
    permission_classes = [IsAdminUser]

    # def perform_destroy(self, instance):
    #     instance.delete()
    def perform_destroy(self, instance):
        instance.hard_delete(self.request.user)

