# import pytest
# from django.contrib.auth import get_user_model
# from rest_framework.test import APIClient
# from order.models import Cart, CartItem, Order
# from store.models import Product, StoreItem, Store, Category

# User = get_user_model()

# # Fixtures
# @pytest.fixture
# def user(db):
#     return User.objects.create_user(username="buyer", password="pass")

# @pytest.fixture
# def seller(db):
#     return User.objects.create_user(username="seller", password="pass")

# @pytest.fixture
# def client(user):
#     c = APIClient()
#     c.force_authenticate(user=user)
#     return c

# @pytest.fixture
# def category(db):
#     return Category.objects.create(name="Tech", slug="tech")

# @pytest.fixture
# def product(db, category):
#     return Product.objects.create(name="Mouse", description="Wireless", category=category)

# @pytest.fixture
# def store(db, seller):
#     return Store.objects.create(name="Tech Hub", seller=seller)

# @pytest.fixture
# def store_item(db, product, store):
#     return StoreItem.objects.create(product=product, store=store, price=10000, stock=20)

# @pytest.fixture
# def cart(db, user):
#     return Cart.objects.create(user=user)

# @pytest.fixture
# def cart_item(db, cart, store_item):
#     return CartItem.objects.create(cart=cart, store_item=store_item, quantity=2)

# # Cart
# @pytest.mark.django_db
# def test_create_cart(client):
#     response = client.post("/api/carts/", {})
#     assert response.status_code in [200, 201]

# # Cart Items
# @pytest.mark.django_db
# def test_add_cart_item(client, store_item):
#     payload = {"store_item": store_item.id, "quantity": 2}
#     res = client.post("/api/cart-items/", payload, format="json")
#     assert res.status_code == 201

# @pytest.mark.django_db
# def test_list_cart_items(client, store_item):
#     client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 1}, format="json")
#     res = client.get("/api/cart-items/")
#     assert res.status_code == 200

# @pytest.mark.django_db
# def test_update_cart_item(client, store_item):
#     res = client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 1}, format="json")
#     cid = res.data["id"]
#     patch = client.patch(f"/api/cart-items/{cid}/", {"quantity": 3}, format="json")
#     assert patch.status_code == 200
#     assert patch.data["quantity"] == 3

# @pytest.mark.django_db
# def test_delete_cart_item(client, store_item):
#     res = client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 1}, format="json")
#     cid = res.data["id"]
#     delete = client.delete(f"/api/cart-items/{cid}/")
#     assert delete.status_code == 204

# # Orders
# @pytest.mark.django_db
# def test_create_order(client, store_item):
#     client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 2}, format="json")
#     res = client.post("/api/orders/", {}, format="json")
#     assert res.status_code == 201

# @pytest.mark.django_db
# def test_list_orders(client, store_item):
#     client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 2}, format="json")
#     client.post("/api/orders/", {}, format="json")
#     res = client.get("/api/orders/")
#     assert res.status_code == 200

# # Order Items
# @pytest.mark.django_db
# def test_list_order_items(client, store_item):
#     client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 1}, format="json")
#     client.post("/api/orders/", {}, format="json")
#     res = client.get("/api/order-items/")
#     assert res.status_code == 200

# # Payments
# @pytest.mark.django_db
# def test_create_payment(client):
#     res = client.post("/api/payments/", {"amount": 30000}, format="json")
#     assert res.status_code == 200

# @pytest.mark.django_db
# def test_verify_payment(client):
#     res = client.get("/api/payments/verify/?Authority=XYZ&Status=OK")
#     assert res.status_code in [200, 400]

# # Seller Dashboards
# @pytest.mark.django_db
# def test_seller_store_items(client, store_item):
#     res = client.get("/api/seller/items/")
#     assert res.status_code == 200

# @pytest.mark.django_db
# def test_seller_orders(client, store_item):
#     client.post("/api/cart-items/", {"store_item": store_item.id, "quantity": 2}, format="json")
#     client.post("/api/orders/", {}, format="json")
#     res = client.get("/api/seller/orders/")
#     assert res.status_code == 200
