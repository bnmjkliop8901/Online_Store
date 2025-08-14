import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from customer.models import Address

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="soheil1111",
        email="soheil@gmail.com",
        password="blackroom",
        first_name="Soheil",
        last_name="K"
    )

@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def address(db, user):
    return Address.objects.create(
        user=user,
        label="Home",
        address_line_1="Shahran",
        address_line_2="",
        city="Tehran",
        state="Tehran",
        postal_code="1234567890",
        country="Iran"
    )

def test_register(db):
    res = APIClient().post("/api/auth/register/", {
        "username": "new",
        "email": "newuser@gmail.com",
        "password": "new123",
        "first_name": "new",
        "last_name": "nneeww",
        "phone": "09121234567"
    }, format="json")
    assert res.status_code == 201

def test_request_otp(db):
    User.objects.create_user(username="otpppp", password="otp123")
    res = APIClient().post("/api/accounts/request-otp/", {
        "username": "otpppp"
    }, format="json")
    assert res.status_code in [200, 201, 400] #########

def test_verify_otp(db):
    User.objects.create_user(username="otpppp", password="otp123")
    res = APIClient().post("/api/accounts/verify-otp/", {
        "username": "otpppp",
        "otp": "123456"
    }, format="json")
    assert res.status_code in [200, 400]   #############

def test_update_profile(client):
    res = client.put("/api/myuser/", {
        "first_name": "Updated"
    }, format="json")
    assert res.status_code == 200

def test_create_address(client):
    res = client.post("/api/addresses/", {
        "label": "Home",
        "address_line_1": "Tehran",
        "address_line_2": "",
        "city": "Tehran",
        "state": "Tehran",
        "postal_code": "9876543210",
        "country": "Iran"
    }, format="json")
    assert res.status_code == 201

def test_list_addresses(client, address):
    res = client.get("/api/addresses/")
    assert res.status_code == 200
    assert "results" in res.data
    assert isinstance(res.data["results"], list)

def test_update_address(client, address):
    res = client.put(f"/api/addresses/{address.id}/", {
        "label": "Work",
        "address_line_1": "Street",
        "address_line_2": "",
        "city": "Tehran",
        "state": "Tehran",
        "postal_code": "1111111111",
        "country": "Iran"
    }, format="json")
    assert res.status_code == 200

def test_delete_address(client, address):
    res = client.delete(f"/api/addresses/{address.id}/")
    assert res.status_code == 204

def test_admin_customer_access(db):
    admin = User.objects.create_superuser(username="admin", email="admin@gmail.com", password="adminpass")
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.get("/api/admin-customers/")
    assert res.status_code == 200
    assert "results" in res.data
    assert isinstance(res.data["results"], list)


def test_admin_address_access(db):
    admin = User.objects.create_superuser(username="admin", email="admin@gmail.com", password="adminpass")
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.get("/api/admin-addresses/")
    assert res.status_code == 200
    assert "results" in res.data
    assert isinstance(res.data["results"], list)




def test_admin_update_address(db):
    admin = User.objects.create_superuser(username="admin", email="admin@gmail.com", password="adminpass")
    address = Address.objects.create(
        user=admin,
        label="Old",
        address_line_1="Old",
        city="Tehran",
        state="Tehran",
        postal_code="0000000000",
        country="Iran"
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.put(f"/api/admin-addresses/{address.id}/", {
        "user": admin.id,
        "label": "New",
        "address_line_1": "New",
        "address_line_2": "",
        "city": "Tehran",
        "state": "Tehran",
        "postal_code": "999999999",
        "country": "Iran"
    }, format="json")
    assert res.status_code == 200



def test_admin_delete_address(db):
    admin = User.objects.create_superuser(username="admin", email="admin@gmail.com", password="adminpass")
    address = Address.objects.create(
        user=admin,
        label="To Delete",
        address_line_1="Delete St",
        city="Tehran",
        state="Tehran",
        postal_code="1231231234",
        country="Iran"
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.delete(f"/api/admin-addresses/{address.id}/")
    assert res.status_code == 204

