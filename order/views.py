from rest_framework import viewsets , status
from django.db import transaction
import requests
from django.http import JsonResponse
from django.conf import settings
from customer.models import Address
from rest_framework.exceptions import ValidationError
from order.models import Cart, CartItem, Order, OrderItem, Payment
from order.serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer , StoreItemSerializer , StoreItem
from rest_framework.permissions import IsAuthenticated
from order.tasks import send_order_received_email , send_payment_confirmed_email
from rest_framework.decorators import api_view, permission_classes , action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny







class SellerOrderViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            items__store_item__store__seller=user
        ).distinct()




class SellerStoreItemViewSet(ReadOnlyModelViewSet):
    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return StoreItem.objects.filter(store__seller=user, is_active=True)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user).prefetch_related('items')



class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(cart__user=user).select_related('store_item', 'cart')

    def partial_update(self, request, pk=None):
        try:
            cart_item = self.get_object()

            if cart_item.cart.user != request.user:
                return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

            new_quantity = request.data.get('quantity')
            if not new_quantity or int(new_quantity) <= 0:
                return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

            if int(new_quantity) > cart_item.store_item.stock:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = int(new_quantity)
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            cart_item = self.get_object()

            if cart_item.cart.user != request.user:
                return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(f"Request made by: {user}, is_seller: {user.is_seller}")

        if user.is_seller:
            return Order.objects.filter(
                items__store_item__store__seller=user
            ).distinct().prefetch_related('items__store_item__product')

        return Order.objects.filter(
            user=user
        ).prefetch_related('items__store_item__product').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        order = serializer.instance
        send_order_received_email.delay(order.user.email, order.id)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = self.request.user

        try:
            cart = Cart.objects.prefetch_related('items__store_item').get(user=user)
        except Cart.DoesNotExist:
            raise ValidationError("Cart not found for this user.")

        if not cart.items.exists():
            raise ValidationError("Your cart is empty.")

        address_id = self.request.data.get("address_id")
        if not address_id:
            raise ValidationError("Missing address_id. Please select one during checkout.")
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise ValidationError("Address not found.")

        for item in cart.items.all():
            if item.quantity > item.store_item.stock:
                raise ValidationError(
                    f"Insufficient stock for {item.store_item.product.name}. "
                    f"Available: {item.store_item.stock}"
                )

        with transaction.atomic():
            total_price = sum(item.total_item_price for item in cart.items.all())

            order = Order.objects.create(
                user=user,
                address=address,
                total_price=total_price
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    store_item=item.store_item,
                    quantity=item.quantity,
                    price=item.unit_price,
                    total_price=item.total_item_price
                )
                item.store_item.stock = max(item.store_item.stock - item.quantity, 0)
                item.store_item.save(update_fields=["stock"])

            cart.items.all().delete()

            serializer.instance = order

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        STATUS_MAP = {
            "PENDING": 1,
            "PROCESSING": 2,
            "DELIVERED": 3,
            "CANCELLED": 4,
            "FAILED": 5,
        }
        allowed_transitions = ["PROCESSING", "DELIVERED"]

        user = request.user
        if not user.is_seller:
            return Response({'error': 'Only sellers can update order status'}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status', '').upper()
        if new_status not in STATUS_MAP or new_status not in allowed_transitions:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order = self.get_object()
        order.status = STATUS_MAP[new_status]
        order.save(update_fields=["status"])

        return Response({'message': 'Order status updated', 'status': new_status}, status=status.HTTP_200_OK)




class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('store_item', 'order')
    serializer_class = OrderItemSerializer



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    data = request.data
    user = request.user


    transaction_id = data.get('transaction_id')
    reference_id = data.get('reference_id')
    card_pan = data.get('card_pan')
    order_id = data.get('order_id')
    amount = data.get('amount')
    fee = data.get('fee')


    if not all([transaction_id, reference_id, card_pan, order_id, amount, fee]):
        return Response({'detail': 'Missing required payment fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)


    payment = Payment.objects.create(
        order=order,
        transaction_id=transaction_id,
        reference_id=reference_id,
        card_pan=card_pan,
        amount=amount,
        fee=fee,
        status=2  
    )


    send_payment_confirmed_email.delay(user.email, order.id)

    return Response({'detail': 'Payment verified and saved successfully.'}, status=status.HTTP_200_OK)








class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        amount = int(order.total_price)
        if amount < 100:
            return Response({"error": "Amount must be at least 100 Toman"}, status=status.HTTP_400_BAD_REQUEST)
    

        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount,
            "callback_url": settings.ZARINPAL_CALLBACK_URL,
            "description": "پرداخت سفارش",
            "metadata": {
                "email": request.user.email,
                "mobile": request.user.phone
            }
        }

        try:
            response = requests.post(
                "https://sandbox.zarinpal.com/pg/v4/payment/request.json",
                json=payload
            )
            result = response.json()
            print("Zarinpal initiation response:", result)

            if result.get("data", {}).get("code") == 100:
                authority = result["data"]["authority"]
                fee = result["data"].get("fee", 0)

                Payment.objects.create(
                    order=order,
                    transaction_id=authority,
                    amount=amount,
                    fee=fee
                )
                return Response({
                    "authority": authority,
                    "url": f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
                })

            return Response({
                "error": "Payment request failed",
                "details": result.get("errors", result.get("data", {}).get("message", "Unapproved request"))
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({
                "error": "Connection to Zarinpal failed",
                "details": str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=["get"], url_path="verify" , permission_classes=[AllowAny])
    def verify_payment(self, request):
        print("View reached")
        print("Params:", request.GET)
        authority = request.GET.get("Authority")
        status_code = request.GET.get("Status")

        if not authority or not status_code:
            return JsonResponse({"error": "Missing parameters"}, status=400)

        try:
            payment = Payment.objects.get(transaction_id=authority)
            order = payment.order
            if status_code == "OK":
                payload = {
                    "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                    "amount": int(payment.amount),
                    "authority": authority
                }
                response = requests.post(
                    "https://sandbox.zarinpal.com/pg/v4/payment/verify.json",
                    json=payload
                )
                result = response.json()
                print("Zarinpal verify response:", result)

                if result.get("data", {}).get("code") == 100:
                    data = result["data"]
                    payment.verified = True
                    payment.ref_id = data.get("ref_id")
                    payment.card_pan = data.get("card_pan")
                    payment.fee = data.get("fee", 0)
                    payment.save()


                    order.status = 2  # PROCESSING or DELIVERED depending on flow
                    order.save(update_fields=["status"])

                    send_payment_confirmed_email.delay(
                        payment.order.user.email,
                        payment.order.id
                    )

                    return JsonResponse({"status": "success", "ref_id": payment.ref_id})

                return JsonResponse({
                    "status": "failed",
                    "message": result.get("errors", result.get("data", {}).get("message", "Verification failed"))
                }, status=400)

            return JsonResponse({"status": "cancelled", "message": "User canceled payment"})

        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)





































































# from rest_framework import viewsets , status
# from django.db import transaction
# import requests
# from django.http import JsonResponse
# from django.conf import settings
# from customer.models import Address
# from rest_framework.exceptions import ValidationError
# from order.models import Cart, CartItem, Order, OrderItem, Payment
# from order.serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer , StoreItemSerializer , StoreItem
# from rest_framework.permissions import IsAuthenticated
# from order.tasks import send_order_received_email , send_payment_confirmed_email
# from rest_framework.decorators import api_view, permission_classes , action
# from rest_framework.response import Response
# from rest_framework.viewsets import ReadOnlyModelViewSet
# from rest_framework.permissions import AllowAny
# from django.shortcuts import get_object_or_404







# class SellerOrderViewSet(ReadOnlyModelViewSet):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Order.objects.filter(
#             items__store_item__store__seller=user
#         ).distinct()




# class SellerStoreItemViewSet(ReadOnlyModelViewSet):
#     serializer_class = StoreItemSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return StoreItem.objects.filter(store__seller=user, is_active=True)





# class CartViewSet(viewsets.ModelViewSet):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user, is_active=True)

#     def list(self, request, *args, **kwargs):
#         cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)


# class CartItemViewSet(viewsets.ModelViewSet):
#     serializer_class = CartItemSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return CartItem.objects.filter(cart__user=user).select_related('store_item', 'cart')

#     @action(detail=False, methods=['get'], url_path='items')
#     def my_cart_items(self, request):
#         cart = Cart.objects.filter(user=request.user, is_active=True).first()
#         items = CartItem.objects.filter(cart=cart)
#         serializer = CartItemSerializer(items, many=True)
#         return Response(serializer.data)

#     @action(detail=True, methods=['post'], url_path='add')
#     def add_to_cart(self, request, pk=None):
#         try:
#             store_item = StoreItem.objects.get(pk=pk)
#             cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)

#             cart_item, created = CartItem.objects.get_or_create(cart=cart, store_item=store_item)
#             if not created:
#                 cart_item.quantity += 1
#             else:
#                 cart_item.quantity = 1

#             cart_item.save()
#             serializer = self.get_serializer(cart_item)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except StoreItem.DoesNotExist:
#             return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

#     def partial_update(self, request, pk=None):
#         try:
#             cart_item = self.get_object()

#             if cart_item.cart.user != request.user:
#                 return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

#             new_quantity = request.data.get('quantity')
#             if not new_quantity or int(new_quantity) <= 0:
#                 return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

#             if int(new_quantity) > cart_item.store_item.stock:
#                 return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

#             cart_item.quantity = int(new_quantity)
#             cart_item.save()
#             serializer = self.get_serializer(cart_item)
#             return Response(serializer.data)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, pk=None):
#         try:
#             cart_item = self.get_object()

#             if cart_item.cart.user != request.user:
#                 return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

#             cart_item.delete()
#             return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# # class CartItemViewSet(viewsets.ModelViewSet):
# #     serializer_class = CartItemSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         return CartItem.objects.filter(cart__user=user).select_related('store_item', 'cart')

# #     def partial_update(self, request, pk=None):
# #         try:
# #             cart_item = self.get_object()

# #             if cart_item.cart.user != request.user:
# #                 return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

# #             new_quantity = request.data.get('quantity')
# #             if not new_quantity or int(new_quantity) <= 0:
# #                 return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

# #             if int(new_quantity) > cart_item.store_item.stock:
# #                 return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

# #             cart_item.quantity = int(new_quantity)
# #             cart_item.save()
# #             serializer = self.get_serializer(cart_item)
# #             return Response(serializer.data)

# #         except Exception as e:
# #             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# #     def destroy(self, request, pk=None):
# #         try:
# #             cart_item = self.get_object()

# #             if cart_item.cart.user != request.user:
# #                 return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

# #             cart_item.delete()
# #             return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)

# #         except Exception as e:
# #             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# #     @action(detail=False, methods=['get'], url_path='items', url_name='mycart-items')
# #     def my_cart_items(self, request):
# #         cart = Cart.objects.filter(user=request.user, is_active=True).first()
# #         items = CartItem.objects.filter(cart=cart)
# #         serializer = CartItemSerializer(items, many=True)
# #         return Response(serializer.data)


# # class OrderViewSet(viewsets.ModelViewSet):
# #     serializer_class = OrderSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         print(f"Request made by: {user}, is_seller: {user.is_seller}")

# #         if user.is_seller:
# #             return Order.objects.filter(
# #                 items__store_item__store__seller=user
# #             ).distinct().prefetch_related('items__store_item__product')

# #         return Order.objects.filter(
# #             user=user
# #         ).prefetch_related('items__store_item__product').order_by('-created_at')

# #     def create(self, request, *args, **kwargs):
# #         serializer = self.get_serializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         self.perform_create(serializer)
# #         order = serializer.instance
# #         send_order_received_email.delay(order.user.email, order.id)
# #         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# #     def perform_create(self, serializer):
# #         user = self.request.user

# #         try:
# #             cart = Cart.objects.prefetch_related('items__store_item').get(user=user)
# #         except Cart.DoesNotExist:
# #             raise ValidationError("Cart not found for this user.")

# #         if not cart.items.exists():
# #             raise ValidationError("Your cart is empty.")

# #         address_id = self.request.data.get("address_id")
# #         if not address_id:
# #             raise ValidationError("Missing address_id. Please select one during checkout.")
# #         try:
# #             address = Address.objects.get(id=address_id, user=user)
# #         except Address.DoesNotExist:
# #             raise ValidationError("Address not found.")

# #         for item in cart.items.all():
# #             if item.quantity > item.store_item.stock:
# #                 raise ValidationError(
# #                     f"Insufficient stock for {item.store_item.product.name}. "
# #                     f"Available: {item.store_item.stock}"
# #                 )

# #         with transaction.atomic():
# #             total_price = sum(item.total_item_price for item in cart.items.all())

# #             order = Order.objects.create(
# #                 user=user,
# #                 address=address,
# #                 total_price=total_price
# #             )

# #             for item in cart.items.all():
# #                 OrderItem.objects.create(
# #                     order=order,
# #                     store_item=item.store_item,
# #                     quantity=item.quantity,
# #                     price=item.unit_price,
# #                     total_price=item.total_item_price
# #                 )
# #                 item.store_item.stock = max(item.store_item.stock - item.quantity, 0)
# #                 item.store_item.save(update_fields=["stock"])

# #             cart.items.all().delete()

# #             serializer.instance = order

# #     @action(detail=True, methods=['patch'])
# #     def update_status(self, request, pk=None):
# #         STATUS_MAP = {
# #             "PENDING": 1,
# #             "PROCESSING": 2,
# #             "DELIVERED": 3,
# #             "CANCELLED": 4,
# #             "FAILED": 5,
# #         }
# #         allowed_transitions = ["PROCESSING", "DELIVERED"]

# #         user = request.user
# #         if not user.is_seller:
# #             return Response({'error': 'Only sellers can update order status'}, status=status.HTTP_403_FORBIDDEN)

# #         new_status = request.data.get('status', '').upper()
# #         if new_status not in STATUS_MAP or new_status not in allowed_transitions:
# #             return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

# #         order = self.get_object()
# #         order.status = STATUS_MAP[new_status]
# #         order.save(update_fields=["status"])

# #         return Response({'message': 'Order status updated', 'status': new_status}, status=status.HTTP_200_OK)


# class OrderViewSet(viewsets.ModelViewSet):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_seller:
#             return Order.objects.filter(
#                 items__store_item__store__seller=user
#             ).distinct().prefetch_related('items__store_item__product')
#         return Order.objects.filter(user=user).prefetch_related('items__store_item__product').order_by('-created_at')

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         address_id = request.data.get("address_id")
#         if not address_id:
#             raise ValidationError("Missing address_id. Please select one during checkout.")
#         address = get_object_or_404(Address, id=address_id, user=user)

#         cart = get_object_or_404(Cart, user=user, is_active=True)
#         if not cart.items.exists():
#             raise ValidationError("Your cart is empty.")

#         for item in cart.items.all():
#             if item.quantity > item.store_item.stock:
#                 raise ValidationError(
#                     f"Insufficient stock for {item.store_item.product.name}. Available: {item.store_item.stock}"
#                 )

#         with transaction.atomic():
#             total_price = sum(item.total_item_price for item in cart.items.all())
#             order = Order.objects.create(user=user, address=address, total_price=total_price)

#             for item in cart.items.all():
#                 OrderItem.objects.create(
#                     order=order,
#                     store_item=item.store_item,
#                     quantity=item.quantity,
#                     price=item.unit_price,
#                     total_price=item.total_item_price
#                 )
#                 item.store_item.stock = max(item.store_item.stock - item.quantity, 0)
#                 item.store_item.save(update_fields=["stock"])

#             cart.items.all().delete()
#             cart.is_active = False
#             cart.save(update_fields=["is_active"])

#             send_order_received_email.delay(order.user.email, order.id)

#         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

#     @action(detail=True, methods=['patch'])
#     def update_status(self, request, pk=None):
#         STATUS_MAP = {
#             "PENDING": 1,
#             "PROCESSING": 2,
#             "DELIVERED": 3,
#             "CANCELLED": 4,
#             "FAILED": 5,
#         }
#         allowed_transitions = ["PROCESSING", "DELIVERED"]

#         user = request.user
#         if not user.is_seller:
#             return Response({'error': 'Only sellers can update order status'}, status=status.HTTP_403_FORBIDDEN)

#         new_status = request.data.get('status', '').upper()
#         if new_status not in STATUS_MAP or new_status not in allowed_transitions:
#             return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

#         order = self.get_object()
#         order.status = STATUS_MAP[new_status]
#         order.save(update_fields=["status"])

#         return Response({'message': 'Order status updated', 'status': new_status}, status=status.HTTP_200_OK)



# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.select_related('store_item', 'order')
#     serializer_class = OrderItemSerializer



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def verify_payment(request):
#     data = request.data
#     user = request.user


#     transaction_id = data.get('transaction_id')
#     reference_id = data.get('reference_id')
#     card_pan = data.get('card_pan')
#     order_id = data.get('order_id')
#     amount = data.get('amount')
#     fee = data.get('fee')


#     if not all([transaction_id, reference_id, card_pan, order_id, amount, fee]):
#         return Response({'detail': 'Missing required payment fields.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         order = Order.objects.get(id=order_id, user=user)
#     except Order.DoesNotExist:
#         return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)


#     payment = Payment.objects.create(
#         order=order,
#         transaction_id=transaction_id,
#         reference_id=reference_id,
#         card_pan=card_pan,
#         amount=amount,
#         fee=fee,
#         status=2  
#     )


#     send_payment_confirmed_email.delay(user.email, order.id)

#     return Response({'detail': 'Payment verified and saved successfully.'}, status=status.HTTP_200_OK)








# # class PaymentViewSet(viewsets.ModelViewSet):
# #     queryset = Payment.objects.all()
# #     serializer_class = PaymentSerializer
# #     permission_classes = [IsAuthenticated]

# #     def create(self, request, *args, **kwargs):
# #         order_id = request.data.get("order_id")
# #         try:
# #             order = Order.objects.get(id=order_id, user=request.user)
# #         except Order.DoesNotExist:
# #             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

# #         amount = int(order.total_price)
# #         if amount < 100:
# #             return Response({"error": "Amount must be at least 100 Toman"}, status=status.HTTP_400_BAD_REQUEST)
    

# #         payload = {
# #             "merchant_id": settings.ZARINPAL_MERCHANT_ID,
# #             "amount": amount,
# #             "callback_url": settings.ZARINPAL_CALLBACK_URL,
# #             "description": "پرداخت سفارش",
# #             "metadata": {
# #                 "email": request.user.email,
# #                 "mobile": request.user.phone
# #             }
# #         }

# #         try:
# #             response = requests.post(
# #                 "https://sandbox.zarinpal.com/pg/v4/payment/request.json",
# #                 json=payload
# #             )
# #             result = response.json()
# #             print("Zarinpal initiation response:", result)

# #             if result.get("data", {}).get("code") == 100:
# #                 authority = result["data"]["authority"]
# #                 fee = result["data"].get("fee", 0)

# #                 Payment.objects.create(
# #                     order=order,
# #                     transaction_id=authority,
# #                     amount=amount,
# #                     fee=fee
# #                 )
# #                 return Response({
# #                     "authority": authority,
# #                     "url": f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
# #                 })

# #             return Response({
# #                 "error": "Payment request failed",
# #                 "details": result.get("errors", result.get("data", {}).get("message", "Unapproved request"))
# #             }, status=status.HTTP_400_BAD_REQUEST)

# #         except requests.RequestException as e:
# #             return Response({
# #                 "error": "Connection to Zarinpal failed",
# #                 "details": str(e)
# #             }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# #     @action(detail=False, methods=["get"], url_path="verify" , permission_classes=[AllowAny])
# #     def verify_payment(self, request):
# #         print("View reached")
# #         print("Params:", request.GET)
# #         authority = request.GET.get("Authority")
# #         status_code = request.GET.get("Status")

# #         if not authority or not status_code:
# #             return JsonResponse({"error": "Missing parameters"}, status=400)

# #         try:
# #             payment = Payment.objects.get(transaction_id=authority)
# #             order = payment.order
# #             if status_code == "OK":
# #                 payload = {
# #                     "merchant_id": settings.ZARINPAL_MERCHANT_ID,
# #                     "amount": int(payment.amount),
# #                     "authority": authority
# #                 }
# #                 response = requests.post(
# #                     "https://sandbox.zarinpal.com/pg/v4/payment/verify.json",
# #                     json=payload
# #                 )
# #                 result = response.json()
# #                 print("Zarinpal verify response:", result)

# #                 if result.get("data", {}).get("code") == 100:
# #                     data = result["data"]
# #                     payment.verified = True
# #                     payment.ref_id = data.get("ref_id")
# #                     payment.card_pan = data.get("card_pan")
# #                     payment.fee = data.get("fee", 0)
# #                     payment.save()


# #                     order.status = 2  # PROCESSING or DELIVERED depending on flow
# #                     order.save(update_fields=["status"])

# #                     send_payment_confirmed_email.delay(
# #                         payment.order.user.email,
# #                         payment.order.id
# #                     )

# #                     return JsonResponse({"status": "success", "ref_id": payment.ref_id})

# #                 return JsonResponse({
# #                     "status": "failed",
# #                     "message": result.get("errors", result.get("data", {}).get("message", "Verification failed"))
# #                 }, status=400)

# #             return JsonResponse({"status": "cancelled", "message": "User canceled payment"})

# #         except Payment.DoesNotExist:
# #             return JsonResponse({"error": "Payment not found"}, status=404)
# #         except Exception as e:
# #             return JsonResponse({"error": str(e)}, status=500)



# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         order_id = request.data.get("order_id")
#         order = get_object_or_404(Order, id=order_id, user=request.user)

#         amount = int(order.total_price)
#         if amount < 100:
#             return Response({"error": "Amount must be at least 100 Toman"}, status=status.HTTP_400_BAD_REQUEST)

#         payload = {
#             "merchant_id": settings.ZARINPAL_MERCHANT_ID,
#             "amount": amount,
#             "callback_url": settings.ZARINPAL_CALLBACK_URL,
#             "description": "پرداخت سفارش",
#             "metadata": {
#                 "email": request.user.email,
#                 "mobile": request.user.phone
#             }
#         }

#         try:
#             response = requests.post("https://sandbox.zarinpal.com/pg/v4/payment/request.json", json=payload)
#             result = response.json()

#             if result.get("data", {}).get("code") == 100:
#                 authority = result["data"]["authority"]
#                 fee = result["data"].get("fee", 0)

#                 Payment.objects.create(
#                     order=order,
#                     transaction_id=authority,
#                     amount=amount,
#                     fee=fee
#                 )
#                 return Response({
#                     "authority": authority,
#                     "url": f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
#                 })

#             return Response({
#                 "error": "Payment request failed",
#                 "details": result.get("errors", result.get("data", {}).get("message", "Unapproved request"))
#             }, status=status.HTTP_400_BAD_REQUEST)

#         except requests.RequestException as e:
#             return Response({
#                 "error": "Connection to Zarinpal failed",
#                 "details": str(e)
#             }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

#     @action(detail=False, methods=["get"], url_path="verify", permission_classes=[AllowAny])
#     def verify_payment(self, request):
#         authority = request.GET.get("Authority")
#         status_code = request.GET.get("Status")

#         if not authority or not status_code:
#             return JsonResponse({"error": "Missing parameters"}, status=400)

#         try:
#             payment = Payment.objects.get(transaction_id=authority)
#             order = payment.order

#             if status_code == "OK":
#                 payload = {
#                     "merchant_id": settings.ZARINPAL_MERCHANT_ID,
#                     "amount": int(payment.amount),
#                     "authority": authority
#                 }
#                 response = requests.post("https://sandbox.zarinpal.com/pg/v4/payment/verify.json", json=payload)
#                 result = response.json()

#                 if result.get("data", {}).get("code") == 100:
#                     data = result["data"]
#                     payment.verified = True
#                     payment.ref_id = data.get("ref_id")
#                     payment.card_pan = data.get("card_pan")
#                     payment.fee = data.get("fee", 0)
#                     payment.save()

#                     order.status = 2  # PROCESSING
#                     order.save(update_fields=["status"])

#                     send_payment_confirmed_email.delay(order.user.email, order.id)

#                     return JsonResponse({"status": "success", "ref_id": payment.ref_id})

#                 return JsonResponse({
#                     "status": "failed",
#                     "message": result.get("errors", result.get("data", {}).get("message", "Verification failed"))
#                 }, status=400)

#             return JsonResponse({"status": "cancelled", "message": "User canceled payment"})

#         except Payment.DoesNotExist:
#             return JsonResponse({"error": "Payment not found"}, status=404)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)









# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework.permissions import IsAuthenticated
# # from .models import Cart, CartItem
# # from .serializers import CartSerializer, CartItemSerializer
# # from django.shortcuts import get_object_or_404

# # class MyCartView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         cart, _ = Cart.objects.get_or_create(user=request.user)
# #         serializer = CartSerializer(cart)
# #         return Response(serializer.data)


# # class CartItemsView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         items = CartItem.objects.filter(cart__user=request.user)
# #         serializer = CartItemSerializer(items, many=True)
# #         return Response(serializer.data)


# # class AddToCartView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, id):
# #         store_item_id = id
# #         quantity = request.data.get("quantity", 1)
# #         serializer = CartItemSerializer(data={"store_item": store_item_id, "quantity": quantity}, context={"request": request})
# #         serializer.is_valid(raise_exception=True)
# #         cart_item = serializer.save()
# #         return Response(CartItemSerializer(cart_item).data)


# # class UpdateCartItemView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def patch(self, request, id):
# #         cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)
# #         quantity = request.data.get("quantity")
# #         if not quantity or int(quantity) <= 0:
# #             return Response({"error": "Invalid quantity"}, status=400)
# #         cart_item.quantity = int(quantity)
# #         cart_item.save()
# #         return Response(CartItemSerializer(cart_item).data)


# # class RemoveCartItemView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def delete(self, request, id):
# #         cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)
# #         cart_item.delete()
# #         return Response({"message": "Item deleted"}, status=204)
