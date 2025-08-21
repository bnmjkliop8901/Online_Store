import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from store.models import Category, Product, ProductImage, Store, StoreItem, Review
from django.contrib.auth import get_user_model
from PIL import Image
import io

User = get_user_model()


def generate_test_image(name="test.jpg"):
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type="image/jpeg")


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", password="testpass", is_seller=True)

@pytest.fixture
def api_client(test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client

@pytest.fixture
def category(db):
    image = generate_test_image("cat.jpg")
    return Category.objects.create(name="Electronics", description="Tech stuff", image=image, is_active=True) 

@pytest.fixture
def product(db, category):
    product = Product.objects.create(name="Phone", description="Smartphone", is_active=True)
    product.categories.add(category)
    return product

@pytest.fixture
def store(db, test_user):
    return Store.objects.create(name="Gadget Store", description="Tech stuff", seller=test_user)

@pytest.fixture
def store_item(db, product, store):
    return StoreItem.objects.create(product=product, store=store, price=20000, stock=5)


@pytest.mark.django_db
def test_category_list(api_client, category):
    response = api_client.get("/api/categories/")
    assert response.status_code == 200
    assert any(cat["name"] == "Electronics" for cat in response.data["results"])

@pytest.mark.django_db
def test_category_create(api_client):
    image = generate_test_image("cat.jpg")
    response = api_client.post("/api/categories/", {
        "name": "Books",
        "description": "All kinds of books",
        "is_active": True,
        "image": image
    }, format="multipart")
    assert response.status_code == 201
    assert response.data["name"] == "Books"

@pytest.mark.django_db
def test_category_tree(api_client, category):
    response = api_client.get("/api/category-tree/")
    assert response.status_code == 200
    assert isinstance(response.data, list)


@pytest.mark.django_db
def test_product_list(api_client, product):
    response = api_client.get("/api/products/")
    assert response.status_code == 200
    assert any(p["name"] == "Phone" for p in response.data["results"])

@pytest.mark.django_db
def test_product_create(api_client, category):
    response = api_client.post("/api/products/", {
        "name": "Laptop",
        "description": "Portable PC",
        "categories": [category.id],
        "is_active": True
    }, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "Laptop"


@pytest.mark.django_db
def test_product_image_upload(api_client, product):
    image = generate_test_image("test.jpg")
    response = api_client.post("/api/product-images/", {
        "product": product.id,
        "image": image
    }, format="multipart")
    assert response.status_code == 201
    assert "image" in response.data


@pytest.mark.django_db
def test_store_list(api_client, store):
    response = api_client.get("/api/mystore/")
    assert response.status_code == 200
    assert any(s["name"] == "Gadget Store" for s in response.data["results"])

@pytest.mark.django_db
def test_store_create(api_client):
    response = api_client.post("/api/mystore/", {
        "name": "Bookstore",
        "description": "Books and more"
    }, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "Bookstore"


@pytest.mark.django_db
def test_store_item_list(api_client, store_item):
    response = api_client.get("/api/store-items/")
    assert response.status_code == 200
    assert any(item["price"] == "20000.00" for item in response.data["results"])

@pytest.mark.django_db
def test_store_item_create(api_client, product, store):
    response = api_client.post("/api/store-items/", {
        "product": product.id,
        "store": store.id,
        "price": 30000,
        "stock": 4
    }, format="json")
    assert response.status_code == 201
    assert response.data["price"] == "30000.00"


@pytest.mark.django_db
def test_review_create_for_product(api_client, product):
    response = api_client.post(f"/api/products/{product.id}/review_create/", {
        "rating": 5,
        "comment": "Excellent product!"
    }, format="json")
    assert response.status_code == 201
    assert response.data["rating"] == 5

@pytest.mark.django_db
def test_review_create_for_store(api_client, store):
    response = api_client.post("/api/reviews/", {
        "store": store.id,
        "rating": 4,
        "comment": "Great service!"
    }, format="json")
    assert response.status_code == 201
    assert response.data["rating"] == 4



@pytest.mark.django_db
def test_seller_store_list(api_client, store):
    response = api_client.get("/api/seller/stores/")
    assert response.status_code == 200
    assert any(s["name"] == "Gadget Store" for s in response.data["results"])

@pytest.mark.django_db
def test_seller_product_list(api_client, product, store):
    StoreItem.objects.create(product=product, store=store, price=10000, stock=10)
    response = api_client.get("/api/seller/products/")
    assert response.status_code == 200
    assert any(p["name"] == "Phone" for p in response.data["results"])


@pytest.mark.django_db
def test_seller_category_create(api_client):
    image = generate_test_image("cat2.jpg")
    response = api_client.post("/api/seller/categories/", {
        "name": "Accessories",
        "description": "Phone accessories",
        "is_active": True,
        "image": image
    }, format="multipart")
    assert response.status_code == 201
    assert response.data["name"] == "Accessories"
