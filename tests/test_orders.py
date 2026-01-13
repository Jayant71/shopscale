from email import header
from fastapi import status
from fastapi.testclient import TestClient
import pytest


def create_authenticated_client(client: TestClient, email: str, password: str, is_admin: bool = False):
    # Register
    client.post("/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User",
        "role": "admin" if is_admin else "customer"
    })

    # Login
    login_data = {"username": email, "password": password}
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_my_orders_authenticated(client: TestClient):
    """Test that a user can retrieve their own orders"""

    headers = create_authenticated_client(
        client, "user@example.com", "userpass")
    response = client.get("/orders/", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_cart_checkout_creates_order(client: TestClient, mock_current_user_admin):
    """Test checking out the cart successfully creates an order and clears the cart"""

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
    response = client.get("/orders/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["order_items"][0]["product_id"] == product_id
    assert data[0]["order_items"][0]["quantity"] == 1
    assert data[0]["total_amount"] == 50.0
    response = client.get("/cart/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0
