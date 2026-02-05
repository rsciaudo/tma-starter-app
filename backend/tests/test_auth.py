"""
Contract-level tests for the /api/auth endpoint
"""

import pytest
from httpx import AsyncClient


# Tests for POST /api/auth/register
@pytest.mark.asyncio
async def test_register_new_user_empty_username_error(client: AsyncClient):
    """Test that POST /api/auth/register requires a username"""
    user_data = {
        "username": "",
        "email": "abc@example.com",
        "password": "password",
        "role": "user",
    }
    response = await client.post("/api/auth/register", json=user_data)
    """Empty username rejected"""
    assert response.status_code == 400
    assert "Username cannot be empty" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_new_user_empty_email_error(client: AsyncClient):
    """Test that POST /api/auth/register requires an email"""
    user_data = {
        "username": "username",
        "email": "",
        "password": "password",
        "role": "user",
    }
    response = await client.post("/api/auth/register", json=user_data)
    """Empty email rejected"""
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_new_user_empty_password_error(client: AsyncClient):
    """Test that POST /api/auth/register requires a password"""
    user_data = {
        "username": "username",
        "email": "abc@example.com",
        "password": "",
        "role": "user",
    }
    response = await client.post("/api/auth/register", json=user_data)
    """Empty password rejected"""
    assert response.status_code == 400
    assert "Password cannot be empty" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_new_user_success(client: AsyncClient):
    """Test that POST /api/auth/register creates a new user
    given the appropriate inputs"""
    user_data = {
        "username": "username",
        "email": "abc@example.com",
        "password": "password",
        "role": "user",
    }
    response = await client.post("/api/auth/register", json=user_data)
    """Created new user"""
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "username"
    assert data["email"] == "abc@example.com"
    assert data["role"]["name"] == "user"
    assert "password" not in data  # Password should not be in response


@pytest.mark.asyncio
async def test_register_new_user_with_admin_role(client: AsyncClient, auth_headers):
    """Test that POST /api/auth/register creates a new admin
    given the appropriate inputs"""
    user_data = {
        "username": "username",
        "email": "abc@example.com",
        "password": "password",
        "role": "admin",
    }
    response = await client.post(
        "/api/auth/register", json=user_data, headers=auth_headers
    )
    """Created new admin user"""
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "username"
    assert data["email"] == "abc@example.com"
    assert data["role"]["name"] == "admin"
    assert "password" not in data  # Password should not be in response


@pytest.mark.asyncio
async def test_register_new_user_with_invalid_role_error(client: AsyncClient):
    """Test that POST /api/auth/register creates a new admin
    given the appropriate inputs"""
    user_data = {
        "username": "username",
        "email": "abc@example.com",
        "password": "password",
        "role": "sillysalmon",
    }
    response = await client.post("/api/auth/register", json=user_data)
    """Role name does not pass validaton"""
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_new_user_with_duplicate_username_error(
    client: AsyncClient, auth_headers
):
    """Test that POST /api/auth/register returns error for duplicate username"""
    user_data = {
        "username": "duplicate",
        "email": "first@example.com",
        "password": "password123",
        "role": "user",
    }
    # Create first user
    create_response = await client.post(
        "/api/auth/register", json=user_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    first_user_id = create_response.json()["id"]

    # Verify the first user was actually created
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "duplicate"

    # Try to create duplicate username (different email)
    user_data["email"] = "second@example.com"
    response = await client.post(
        "/api/auth/register", json=user_data, headers=auth_headers
    )
    assert response.status_code == 400
    assert "username already registered" in response.json()["detail"].lower()

    # Verify the first user still exists and wasn't affected
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert (
        get_response.json()["email"] == "first@example.com"
    )  # Original email unchanged


@pytest.mark.asyncio
async def test_register_new_user_with_duplicate_email_error(
    client: AsyncClient, auth_headers
):
    """Test that POST /api/auth/register returns error for duplicate email"""
    user_data = {
        "username": "username",
        "email": "duplicate@example.com",
        "password": "password123",
        "role": "user",
    }
    # Create first user
    create_response = await client.post(
        "/api/auth/register", json=user_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    first_user_id = create_response.json()["id"]

    # Verify the first user was actually created
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "username"

    # Try to create duplicate email (different username)
    user_data["username"] = "username2"
    response = await client.post(
        "/api/auth/register", json=user_data, headers=auth_headers
    )
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()

    # Verify the first user still exists and wasn't affected
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "username"  # Original username unchanged


# Tests for POST /api/auth/login
@pytest.mark.asyncio
async def test_login_with_proper_credentials_returns_access_token(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that POST /api/auth/login successfully logs in
    with proper username/password"""

    user_data = {
        "username": regular_user.username,
        "password": regular_user.plaintext_password,
    }
    # Verify the login is successful
    response = await client.post("/api/auth/login", json=user_data)
    assert response.status_code == 200

    assert response.json()["access_token"] is not None


@pytest.mark.asyncio
async def test_login_with_empty_username_returns_error(
    client: AsyncClient, regular_user
):
    """Test that POST /api/auth/login returns 401 Unauthorized
    when given an empty username"""
    user_data = {"username": "", "password": regular_user.plaintext_password}
    response = await client.post("/api/auth/login", json=user_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_empty_password_returns_error(
    client: AsyncClient, regular_user
):
    """Test that POST /api/auth/login returns 401 Unauthorized
    when given an empty password"""
    user_data = {"username": regular_user.username, "password": ""}
    response = await client.post("/api/auth/login", json=user_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_incorrect_password_returns_error(
    client: AsyncClient, regular_user
):
    """Test that POST /api/auth/login returns 401 Unauthorized
    when given an incorrect password"""
    user_data = {"username": regular_user.username, "password": "notpassword"}
    response = await client.post("/api/auth/login", json=user_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_disabled_acc_returns_error(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that POST /api/auth/login returns 403 Forbidden
    when logging into a disabled account"""
    # Deactivate account
    user_id = regular_user.id
    status_data = {"user_id": user_id, "is_active": False}
    get_response = await client.patch(
        f"/api/users/{user_id}/status", headers=auth_headers, json=status_data
    )
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] == 0

    # Attempt to log into deactivated account
    user_data = {
        "username": regular_user.username,
        "password": regular_user.plaintext_password,
    }
    response = await client.post("/api/auth/login", json=user_data)
    assert response.status_code == 403
    # Returns 403 Forbidden


# Tests for GET /api/auth/me
@pytest.mark.asyncio
async def test_get_current_info_returns_user_info(
    client: AsyncClient, user_auth_headers, regular_user
):
    """Test that GET /api/auth/me returns proper user info
    when given bearer token authentication"""

    # Get current user data
    response = await client.get("/api/auth/me", headers=user_auth_headers)
    assert response.status_code == 200

    # Check that the data retrieved is what it should be
    retrieved_data = response.json()
    assert retrieved_data["username"] == regular_user.username
    assert retrieved_data["email"] == regular_user.email
    assert retrieved_data["role"]["id"] == regular_user.role_id
    assert retrieved_data["is_active"] == regular_user.is_active


@pytest.mark.asyncio
async def test_get_current_info_requires_bearer_token_authentication(
    client: AsyncClient,
):
    """Test that GET /api/auth/me returns 401 Unauthorized
    when not given bearer token authentication"""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


# Tests for GET /api/auth/users
@pytest.mark.asyncio
async def test_get_users_gets_users_given_admin_role(client: AsyncClient, auth_headers):
    """Test that GET /api/auth/users returns a list of users when authenticatied"""

    response = await client.get("/api/auth/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Verify the list contains at least the admin user we created
    assert len(data) >= 1
    # Verify each item in the list has the expected user structure
    for user in data:
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "role" in user
        assert "password" not in user  # Password should never be in response

    # Verify the admin user is in the list
    admin_usernames = [user["username"] for user in data]
    assert "admin" in admin_usernames


@pytest.mark.asyncio
async def test_get_all_users_requires_auth(client: AsyncClient):
    """Test that GET /api/auth/users requires authentication"""
    response = await client.get("/api/auth/users")
    assert response.status_code == 401
