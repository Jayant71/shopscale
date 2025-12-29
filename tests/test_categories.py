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

def test_create_category_admin_only(client: TestClient):
    """Test that only admins can create categories"""
    admin_headers = create_authenticated_client(client, "admin_cat@example.com", "adminpass", is_admin=True)
    user_headers = create_authenticated_client(client, "user_cat@example.com", "userpass", is_admin=False)

    cat_data = {"name": "Fashion", "description": "Clothing and accessories"}

    # Failure: Regular user
    response = client.post("/categories/", json=cat_data, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Success: Admin user
    response = client.post("/categories/", json=cat_data, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Fashion"

def test_get_categories_public(client: TestClient):
    """Test that categories are publicly readable"""
    # Assuming "Fashion" was created in the previous test
    response = client.get("/categories/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_update_category_admin_only(client: TestClient):
    """Test that only admins can update categories"""
    admin_headers = create_authenticated_client(client, "admin_upd@example.com", "adminpass", is_admin=True)
    user_headers = create_authenticated_client(client, "user_upd@example.com", "userpass", is_admin=False)

    # First create a category
    resp = client.post("/categories/", json={"name": "Books", "description": "All kinds of books"}, headers=admin_headers)
    cat_id = resp.json()["id"]

    # Failure: Regular user
    response = client.put(f"/categories/{cat_id}", json={"name": "Rare Books"}, headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Success: Admin user
    response = client.put(f"/categories/{cat_id}", json={"name": "Textbooks"}, headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Textbooks"

def test_delete_category_admin_only(client: TestClient):
    """Test that only admins can delete categories"""
    admin_headers = create_authenticated_client(client, "admin_del@example.com", "adminpass", is_admin=True)
    user_headers = create_authenticated_client(client, "user_del@example.com", "userpass", is_admin=False)

    # First create a category
    resp = client.post("/categories/", json={"name": "Toys", "description": "For kids"}, headers=admin_headers)
    cat_id = resp.json()["id"]

    # Failure: Regular user
    response = client.delete(f"/categories/{cat_id}", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Success: Admin user
    response = client.delete(f"/categories/{cat_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
