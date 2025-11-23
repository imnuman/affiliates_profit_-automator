"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    """Test user signup"""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "full_name": "New User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_user):
    """Test signup with duplicate email"""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",  # Already exists
            "password": "NewPassword123!",
            "full_name": "Duplicate User"
        }
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "Password123!"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    """Test token refresh"""
    # Login first
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refresh with invalid token"""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers):
    """Test logout"""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth(client: AsyncClient):
    """Test accessing protected endpoint without authentication"""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_auth(client: AsyncClient, auth_headers):
    """Test accessing protected endpoint with authentication"""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
