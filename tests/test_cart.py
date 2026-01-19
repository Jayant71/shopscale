from pydoc import cli
import re
from urllib import response
from fastapi.testclient import TestClient
from fastapi import status


def create_authenticated_client(client: TestClient, email: str, password: str, is_admin: bool = False):
    client.post("/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Admin" if is_admin else "Test User",
        "role": "admin" if is_admin else "customer"
    })

    login_data = {"username": email, "password": password}
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_cart_items_unauthenticated(client: TestClient):
    """Test cart is inaccessible when unauthenticated"""

    response = client.get("/cart/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_cart_items_authenticated_empty(client: TestClient):
    """Test retrieving cart items for an authenticated user with an empty cart"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    print(data)
    assert data == []


def test_add_item_to_cart_success(client: TestClient, mock_current_user_admin):
    """Test adding an item to the cart successfully"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")
    response = client.post("/products/", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": 100.0,
        "stock_quantity": 10,
        "category_id": 1
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    response = client.post("/cart/add", json={
        "product_id": product_id
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == product_id
    assert data[0]["quantity"] == 1


def test_add_same_item_to_cart_success(client: TestClient, mock_current_user_admin):
    """Test adding an item to the cart successfully twice increases quantity"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")
    response = client.post("/products/", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": 100.0,
        "stock_quantity": 10,
        "category_id": 1
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    response = client.post("/cart/add", json={
        "product_id": product_id
    }, headers=headers)
    response = client.post("/cart/add", json={
        "product_id": product_id
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == product_id
    assert data[0]["quantity"] == 2


def test_add_item_to_cart_not_in_inventory(client: TestClient, mock_current_user_admin):
    """Test adding an item to the cart that is not in inventory"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")

    response = client.post("/cart/add", json={
        "product_id": 9999
    }, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_item_to_cart_out_of_stock(client: TestClient, mock_current_user_admin):
    """Test adding an item to the cart that is out of stock"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")
    response = client.post("/products/", json={
        "name": "Test Product 3",
        "description": "A product",
        "price": 100.0,
        "stock_quantity": 0,
        "category_id": 3
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    response = client.post("/cart/add", json={
        "product_id": product_id
    }, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_cart_items_authenticated_with_items(client: TestClient, mock_current_user_admin):
    """Test retrieving cart items for an authenticated user with items in the cart"""

    headers = create_authenticated_client(
        client, "user1@example.com", "testpassword")

    response = client.post("/products/", json={
        "name": "Test Product 3",
        "description": "A product",
        "price": 100.0,
        "stock_quantity": 10,
        "category_id": 3
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    client.post("/cart/", json={
        "product_id": product_id
    }, headers=headers)
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == product_id
    assert data[0]["quantity"] == 1


def test_delete_item_from_cart_success(client: TestClient, mock_current_user_admin):
    """Test removing an item from the cart successfully"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")
    response = client.post("/products/", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": 100.0,
        "stock_quantity": 10,
        "category_id": 1
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    client.post("/cart/", json={
        "product_id": product_id
    }, headers=headers)
    response = client.delete(
        "/cart/", params={"product_remove": product_id}, headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_delete_item_from_cart_not_present_in_cart(client: TestClient, mock_current_user_admin):
    """Test removing an item from the cart successfully when item is not present in cart"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")

    response = client.delete(
        "/cart/", params={"product_remove": 9999}, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_item_from_cart_exceeding_quantity(client: TestClient, mock_current_user_admin):
    """Test removing an item from the cart exceeding the quantity present"""

    headers = create_authenticated_client(
        client, "user@example.com", "testpassword")
    response = client.post("/products/", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": 100.0,
        "stock_quantity": 10,
        "category_id": 1
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    client.post("/cart/", json={
        "product_id": product_id
    }, headers=headers)
    response = client.delete(
        "/cart/", params={"product_remove": product_id, "quantity": 5}, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cart_checkout_success(client: TestClient, mock_current_user_admin):
    """Test checking out the cart successfully"""

    headers = create_authenticated_client(
        client, "user@example.com", "userpass")
    response = client.post("/products/", json={
        "name": "Checkout Product",
        "description": "A product for checkout testing",
        "price": 50.0,
        "stock_quantity": 5,
        "category_id": 2
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    client.post("/cart/", json={
        "product_id": product_id
    }, headers=headers)
    response = client.get("/cart/checkout", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"]  # type: ignore
    assert len(data["order_items"]) == 1
    assert data["order_items"][0]["product_id"] == product_id
    assert data["order_items"][0]["quantity"] == 1
    assert data["total_amount"] == 50.0
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_cart_checkout_empty_cart(client: TestClient, mock_current_user_admin):
    """Test checking out an empty cart"""

    headers = create_authenticated_client(
        client, "user@example.com", "userpass")
    response = client.post("/products/", json={
        "name": "Checkout Product",
        "description": "A product for checkout testing",
        "price": 50.0,
        "stock_quantity": 5,
        "category_id": 2
    }, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    product_id = response.json()["id"]
    client.post("/cart/", json={
        "product_id": product_id
    }, headers=headers)
    client.delete(
        "/cart/", params={"product_remove": product_id}, headers=headers)
    response = client.get("/cart/checkout", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Cart is empty"


def test_cart_checkout_no_cart(client: TestClient, mock_current_user_admin):
    """Test checking out when no cart exists for the user"""

    headers = create_authenticated_client(
        client, "user@example.com", "userpass")
    response = client.get("/cart/checkout", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Cart not found"
