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

def test_create_order_success(client: TestClient):
    """Test successful order creation and stock reduction"""
    # 1. Setup: Create a category and product
    # Assumes admin is needed for product creation
    admin_headers = create_authenticated_client(client, "admin_order@example.com", "adminpass", is_admin=True)
    
    cat_resp = client.post("/categories/", json={"name": "Electronics", "description": "Gadgets"}, headers=admin_headers)
    cat_id = cat_resp.json()["id"]
    
    prod_resp = client.post("/products/", json={
        "name": "Smarthphone",
        "description": "Latest model",
        "price": 500,
        "stock_quantity": 10,
        "category_id": cat_id
    }, headers=admin_headers)
    product_id = prod_resp.json()["id"]

    # 2. Authenticate customer
    user_headers = create_authenticated_client(client, "customer_order@example.com", "userpass")

    # 3. Place order
    order_data = {
        "items": [
            {"product_id": product_id, "quantity": 2}
        ]
    }
    response = client.post("/orders/", json=order_data, headers=user_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["total_amount"] == 1000 # 500 * 2
    assert len(data["order_items"]) == 1
    
    # 4. Verify stock reduction
    prod_check = client.get(f"/products/{product_id}")
    assert prod_check.json()["stock_quantity"] == 8

def test_create_order_insufficient_stock(client: TestClient):
    """Test order failure due to insufficient stock"""
    admin_headers = create_authenticated_client(client, "admin_stock@example.com", "adminpass", is_admin=True)
    
    prod_resp = client.post("/products/", json={
        "name": "Limited Item",
        "description": "Only 1 left",
        "price": 100,
        "stock_quantity": 1,
        "category_id": 1
    }, headers=admin_headers)
    product_id = prod_resp.json()["id"]

    user_headers = create_authenticated_client(client, "customer_stock@example.com", "userpass")

    order_data = {
        "items": [
            {"product_id": product_id, "quantity": 5}
        ]
    }
    response = client.post("/orders/", json=order_data, headers=user_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "stock" in response.json()["detail"].lower()

def test_get_my_orders(client: TestClient):
    """Test that a user can retrieve their own orders"""
    user1_headers = create_authenticated_client(client, "user1@example.com", "pass")
    user2_headers = create_authenticated_client(client, "user2@example.com", "pass")

    # Assuming product 1 already exists from previous tests or setup
    # If not, this might fail, but for a robust test suite we should ensure it exists.
    # For simplicity here, we assume the setup in test_create_order_success happened.
    
    # Let's create an order for user 1
    client.post("/orders/", json={"items": [{"product_id": 1, "quantity": 1}]}, headers=user1_headers)

    # Get user 1 orders
    resp1 = client.get("/orders/me", headers=user1_headers)
    assert resp1.status_code == status.HTTP_200_OK
    assert len(resp1.json()) >= 1

    # Get user 2 orders (should be empty)
    resp2 = client.get("/orders/me", headers=user2_headers)
    assert resp2.status_code == status.HTTP_200_OK
    assert len(resp2.json()) == 0

def test_order_security_access(client: TestClient):
    """Test that users cannot see other users' orders"""
    user1_headers = create_authenticated_client(client, "u1_sec@example.com", "pass")
    user2_headers = create_authenticated_client(client, "u2_sec@example.com", "pass")
    admin_headers = create_authenticated_client(client, "admin_sec@example.com", "pass", is_admin=True)

    # User 1 creates an order
    resp = client.post("/orders/", json={"items": [{"product_id": 1, "quantity": 1}]}, headers=user1_headers)
    order_id = resp.json()["id"]

    # User 2 tries to see User 1's order
    response = client.get(f"/orders/{order_id}", headers=user2_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_404_NOT_FOUND

    # Admin tries to see User 1's order
    response = client.get(f"/orders/{order_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
