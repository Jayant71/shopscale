from fastapi import status
from fastapi.testclient import TestClient
import pytest

def create_authenticated_client(client: TestClient, email: str, password: str, is_admin: bool = False):
    # Role-based registration
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

def test_create_product_admin_success(client: TestClient):
    """Test that an admin can create a product"""
    headers = create_authenticated_client(client, "admin_prod@example.com", "adminpass", is_admin=True)
    
    response = client.post(
        "/products/",
        json={
            "name": "Admin Laptop",
            "description": "High end",
            "price": 1500,
            "stock_quantity": 5,
            "category_id": 1
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Admin Laptop"

def test_create_product_user_forbidden(client: TestClient):
    """Test that a regular user cannot create a product"""
    headers = create_authenticated_client(client, "user_prod@example.com", "userpass", is_admin=False)
    
    response = client.post(
        "/products/",
        json={
            "name": "User Laptop",
            "description": "No access",
            "price": 500,
            "stock_quantity": 5,
            "category_id": 1
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_read_products_public(client: TestClient):
    """Test that products can be read without authentication"""
    response = client.get("/products/")
    assert response.status_code == status.HTTP_200_OK

def test_update_product_admin_only(client: TestClient):
    """Test that only admins can update products"""
    admin_headers = create_authenticated_client(client, "admin_upd_p@example.com", "pass", is_admin=True)
    user_headers = create_authenticated_client(client, "user_upd_p@example.com", "pass", is_admin=False)

    # Admin creates product
    resp = client.post("/products/", json={
        "name": "Initial Name", "price": 100, "stock_quantity": 10, "category_id": 1
    }, headers=admin_headers)
    prod_id = resp.json()["id"]

    # User try update - fail
    response = client.put(f"/products/{prod_id}", json={"name": "Hacked Name"}, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Admin update - success
    response = client.put(f"/products/{prod_id}", json={"name": "Correct Name"}, headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Correct Name"

def test_delete_product_admin_only(client: TestClient):
    """Test that only admins can delete products"""
    admin_headers = create_authenticated_client(client, "admin_del_p@example.com", "pass", is_admin=True)
    user_headers = create_authenticated_client(client, "user_del_p@example.com", "pass", is_admin=False)

    # Admin creates product
    resp = client.post("/products/", json={
        "name": "To be deleted", "price": 10, "stock_quantity": 1, "category_id": 1
    }, headers=admin_headers)
    prod_id = resp.json()["id"]

    # User try delete - fail
    response = client.delete(f"/products/{prod_id}", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Admin delete - success
    response = client.delete(f"/products/{prod_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT