# import pytest
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
# from customer.models import Address

# User = get_user_model()

# @pytest.fixture
# def user(db):
#     return User.objects.create_user(
#         username="soheil123",
#         email="soheil@example.com",
#         password="testpass123",
#         first_name="Soheil",
#         last_name="Engineer"
#     )

# @pytest.fixture
# def client(user):
#     client = APIClient()
#     client.force_authenticate(user=user)
#     return client

# @pytest.fixture
# def address(db, user):
#     return Address.objects.create(
#         user=user,
#         label="Home",
#         address_line_1="Valiasr Street",
#         address_line_2="",
#         city="Tehran",
#         state="Tehran",
#         postal_code="1234567890",
#         country="Iran"
#     )

# def test_register(db):
#     res = APIClient().post("/api/auth/register/", {
#         "username": "newuser",
#         "email": "newuser@example.com",
#         "password": "newpass123",
#         "first_name": "New",
#         "last_name": "User",
#         "phone": "09121234567"
#     }, format="json")
#     assert res.status_code == 201

# def test_request_otp(db):
#     User.objects.create_user(username="otpuser", password="otp123")
#     res = APIClient().post("/api/accounts/request-otp/", {
#         "username": "otpuser"
#     }, format="json")
#     assert res.status_code in [200, 201, 400]

# def test_verify_otp(db):
#     User.objects.create_user(username="otpuser", password="otp123")
#     res = APIClient().post("/api/accounts/verify-otp/", {
#         "username": "otpuser",
#         "otp": "123456"
#     }, format="json")
#     assert res.status_code in [200, 400]

# def test_update_profile(client):
#     res = client.put("/api/myuser/", {
#         "first_name": "Updated"
#     }, format="json")
#     assert res.status_code == 200

# def test_create_address(client):
#     res = client.post("/api/addresses/", {
#         "label": "Home",
#         "address_line_1": "Valiasr Street",
#         "address_line_2": "",
#         "city": "Tehran",
#         "state": "Tehran",
#         "postal_code": "9876543210",
#         "country": "Iran"
#     }, format="json")
#     assert res.status_code == 201

# def test_list_addresses(client, address):
#     res = client.get("/api/addresses/")
#     assert res.status_code == 200
#     assert "results" in res.data
#     assert isinstance(res.data["results"], list)

# def test_update_address(client, address):
#     res = client.put(f"/api/addresses/{address.id}/", {
#         "label": "Work",
#         "address_line_1": "Enghelab Street",
#         "address_line_2": "",
#         "city": "Tehran",
#         "state": "Tehran",
#         "postal_code": "1111111111",
#         "country": "Iran"
#     }, format="json")
#     assert res.status_code == 200

# def test_delete_address(client, address):
#     res = client.delete(f"/api/addresses/{address.id}/")
#     assert res.status_code == 204

# def test_admin_customer_access(db):
#     admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass")
#     client = APIClient()
#     client.force_authenticate(user=admin)
#     res = client.get("/api/admin-customers/")
#     assert res.status_code == 200
#     assert "results" in res.data
#     assert isinstance(res.data["results"], list)

# def test_admin_address_access(db):
#     admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass")
#     client = APIClient()
#     client.force_authenticate(user=admin)
#     res = client.get("/api/admin-addresses/")
#     assert res.status_code == 200
#     assert "results" in res.data
#     assert isinstance(res.data["results"], list)
