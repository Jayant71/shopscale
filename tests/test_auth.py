from fastapi import status
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    """Test successful user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["id"] is not None
    assert data["is_active"] is True
    assert "hashed_password" not in data  # Should not return password


def test_register_user_duplicate_email(client: TestClient):
    """Test registration with already existing email"""
    # First create a user
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword"
    }
    client.post("/auth/register", json=user_data)

    # Try to register again with same email
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


def test_login_user_success(client: TestClient):
    """Test successful user login"""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "password": "testpassword"
    }
    client.post("/auth/register", json=user_data)

    # Now login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_wrong_email(client: TestClient):
    """Test login with non-existent email"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email not registered"


def test_login_user_wrong_password(client: TestClient):
    """Test login with wrong password"""
    # First register a user
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword"
    }
    client.post("/auth/register", json=user_data)

    # Try to login with wrong password
    login_data = {
        "username": user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Wrong password"


def test_get_all_users_unauthenticated(client: TestClient):
    """Test getting all users without authentication"""
    response = client.get("/auth/users")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_all_users_authenticated_customer(client: TestClient):
    """Test getting all users with regular customer authentication (should fail)"""
    # First register and login a user
    user_data = {
        "email": "customer@example.com",
        "password": "testpassword",
    }
    client.post("/auth/register", json=user_data)

    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Now get users with token - should be 403 Forbidden
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_all_users_authenticated_admin(client: TestClient, mock_current_user_admin):
    """Test getting all users with admin authentication (should succeed)"""
    # First register and login an admin
    admin_data = {
        "email": "admin@example.com",
        "password": "adminpassword",
    }
    client.post("/auth/register", json=admin_data)

    login_data = {
        "username": admin_data["email"],
        "password": admin_data["password"]
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Now get users with admin token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
