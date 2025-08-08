import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from store.models import Store, Product, StoreItem
from customer.models import Address
from order.models import Cart, CartItem, Order, Payment
from order.tasks import send_order_received_email, send_payment_confirmed_email

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="testpass123",
        first_name="Buyer",
        last_name="User",
        phone="09121234567"
    )

@pytest.fixture
def seller(db):
    return User.objects.create_user(
        username="seller",
        email="seller@example.com",
        password="sellerpass123",
        first_name="Seller",
        last_name="User",
        is_seller=True
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass"
    )

@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def seller_client(seller):
    client = APIClient()
    client.force_authenticate(user=seller)
    return client

@pytest.fixture
def admin_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client

@pytest.fixture
def address(user):
    return Address.objects.create(
        user=user,
        label="Home",
        address_line_1="Valiasr",
        city="Tehran",
        state="Tehran",
        postal_code="1234567890",
        country="Iran"
    )

@pytest.fixture
def store(seller):
    return Store.objects.create(name="Test Store", seller=seller)

@pytest.fixture
def product():
    return Product.objects.create(name="Test Product", description="A test product")

@pytest.fixture
def store_item(store, product):
    return StoreItem.objects.create(
        store=store,
        product=product,
        price=100000,
        stock=10,
        is_active=True
    )

@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)

@pytest.fixture
def cart_item(cart, store_item):
    return CartItem.objects.create(
        cart=cart,
        store_item=store_item,
        quantity=2,
        unit_price=store_item.price,
        total_item_price=store_item.price * 2,
        total_discount=0
    )

# 🛒 Cart Tests
def test_cart_list(client):
    res = client.get("/api/carts/")
    assert res.status_code == 200

def test_add_cart_item(client, store_item):
    res = client.post("/api/cart-items/", {
        "store_item": store_item.id,
        "quantity": 1
    }, format="json")
    assert res.status_code == 201


def test_order_creation(client, address, cart_item):
    res = client.post("/api/orders/", {
        "address_id": address.id
    }, format="json")
    assert res.status_code == 201
    assert "id" in res.data

def test_order_list(client):
    res = client.get("/api/orders/")
    assert res.status_code == 200

def test_seller_order_list(seller_client):
    res = seller_client.get("/api/seller/orders/")
    assert res.status_code == 200


def test_payment_initiation(client, address, cart_item):
    order_res = client.post("/api/orders/", {"address_id": address.id}, format="json")
    order_id = order_res.data["id"]

    res = client.post("/api/payments/", {"order_id": order_id}, format="json")
    assert res.status_code == 200
    assert "authority" in res.data

def test_payment_verification(client, address, cart_item):
    order_res = client.post("/api/orders/", {"address_id": address.id}, format="json")
    order_id = order_res.data["id"]

    Payment.objects.create(
        order_id=order_id,
        transaction_id="TX123456",
        reference_id="REF123456",
        card_pan="603799******1234",
        amount=200000,
        fee=5000,
        status=1
    )

    res = client.get("/api/payments/verify/", {
        "Authority": "TX123456",
        "Status": "OK"
    })
    assert res.status_code in [200, 400]


def test_payment_invalid_order(client):
    res = client.post("/api/payments/", {"order_id": 9999}, format="json")
    assert res.status_code == 404

def test_payment_low_amount(client, address, cart_item):
    cart_item.quantity = 1
    cart_item.total_item_price = 50
    cart_item.save()

    res = client.post("/api/orders/", {"address_id": address.id}, format="json")
    order_id = res.data["id"]

    res = client.post("/api/payments/", {"order_id": order_id}, format="json")
    assert res.status_code == 400


def test_send_order_received_email(user):
    result = send_order_received_email.apply(args=[user.email, 1])
    assert result.successful()

def test_send_payment_confirmed_email(user):
    result = send_payment_confirmed_email.apply(args=[user.email, 1])
    assert result.successful()


def test_model_strs(user, address, store_item, cart_item):
    assert str(cart_item.cart) != ""
    assert str(cart_item) != ""
    assert str(store_item) != ""
    assert str(address) != ""


def test_admin_changelist_views(admin_client):
    for model, model_admin in site._registry.items():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        url = reverse(f"admin:{app_label}_{model_name}_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200
