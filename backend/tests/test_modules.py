"""
Contract-level tests for the /api/modules endpoint
"""

import pytest
from httpx import AsyncClient


#helper function
def assert_module_shape(m: dict):
    assert "id" in m
    assert "title" in m
    assert "description" in m
    assert "created_at" in m
    assert "updated_at" in m


#fixtures
@pytest.fixture
async def user_headers(client: AsyncClient, auth_headers):
    """Cretes or reuses a regular user and returns auth headers for that user"""
    username = "modules_test_user"
    password = "password123"
    email = "modules_test_user@example.com"

    #create user as admin 
    create_resp = await client.post(
        "/api/users",
        json = {"username": username, "email": email, "password": password, 
                "role": "user"},
        headers = auth_headers
    )
    #when rerunning tests, user might exist already (400)
    assert create_resp.status_code in (201, 400), create_resp.text

    #login as the user
    login_resp = await client.post(
        "/api/auth/login",
        json = {"username": username, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text

    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


#GET /api/modules (list modules)


@pytest.mark.asyncio
async def test_get_modules_requires_auth(client: AsyncClient):
    """GET /api/modules requires authentication"""
    resp = await client.get("/api/modules")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_modules_success_as_admin_returns_list(client: AsyncClient, auth_headers):
    """Admin can GET /api/modules and receives list"""
    resp = await client.get("/api/modules", headers = auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

    for m in data:
        assert_module_shape(m)


@pytest.mark.asyncio
async def test_get_modules_as_user_returns_list(client: AsyncClient, user_headers):
    """Regular user can GET /api/modules and receive list"""
    resp = await client.get("/api/modules", headers = user_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

    for m in data:
        assert_module_shape(m)


@pytest.mark.asyncio
async def test_get_modules_invalid_422(client: AsyncClient, auth_headers):
    """Test that GET /api/modules returns 422 for invalid query params"""
    resp = await client.get(
        "/api/modules?course_id=abc", 
        headers = auth_headers
    )
    assert resp.status_code == 422


#GET /api/modules{id} (get single module)


@pytest.mark.asyncio
async def test_get_module_requires_auth(client: AsyncClient):
    """GET /api/modules/{id} requires authentication"""
    resp = await client.get("/api/modules/1")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_module_not_found(client: AsyncClient, user_headers):
    """GET /api/modules/{id} returns 404 for non existent module"""
    resp = await client.get("/api/modules/123456", headers = user_headers)
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Module not found"


@pytest.mark.asyncio
async def test_get_module_string_id_422(client: AsyncClient, auth_headers):
    """GET /api/modules/{id} returns 422 for invalid id type"""
    resp = await client.get("/api/modules/{id}", headers = auth_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_module_success(client: AsyncClient, auth_headers, user_headers):
    """Create a module then GET by id"""
    create = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "Test2", "description": "x"}},
        headers = auth_headers
    )
    assert create.status_code == 201, create.text
    module_id = create.json()["id"]

    resp = await client.get(f"/api/modules/{module_id}", headers = user_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert_module_shape(data)



#POST /api/modules (create module)


@pytest.mark.asyncio
async def test_create_module_requires_auth(client: AsyncClient):
    """POST /api/modules/ requires authentication"""
    resp = await client.post(
        "/api/modules", 
        json = {"module_data": {"title": "x"}}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_module_forbidden_for_non_admin(client: AsyncClient, user_headers):
    """Regular user can't POST api/modules"""
    resp = await client.post(
        "/api/modules", 
        json = {"module_data": {"title": "x"}}, 
        headers = user_headers
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_module_invalid_body_422(client: AsyncClient, auth_headers):
    """POST /api/modules returns 422 for missing required fields"""
    resp = await client.post(
        "/api/modules", 
        json = {}, 
        headers = auth_headers
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_module_success_admin_201(client: AsyncClient, auth_headers):
    """Admin can POST /api/modules with valid data"""
    resp = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "Test Module", "description": "test"}},
        headers = auth_headers
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert_module_shape(data)
    assert data["title"] == "Test Module"
    assert data["description"] == "test"


#PATCH /api/modules/{id} (update module)


@pytest.mark.asyncio
async def test_update_module_requires_auth(client: AsyncClient):
    """PATCH /api/modules/{id} requires authentication"""
    resp = await client.patch("/api/modules/1", json = {"module_data": {"title": "Updated"}})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_module_forbidden_for_non_admin(client: AsyncClient, auth_headers, user_headers):
    """Regular user can't PATCH /api/modules/{id}"""
    create = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "Patch Target", "description": "x"}},
        headers = auth_headers
    )
    assert create.status_code == 201, create.text
    module_id = create.json()["id"]

    resp = await client.patch(
        f"/api/modules/{module_id}",
        json = {"module_data": {"title": "No"}},
        headers = user_headers
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_module_invalid_body_422(client: AsyncClient, auth_headers):
    """PATCH /api/modules/{id} returns 422 for invalid body types"""
    create = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "Patch Invalid Body 422", "description": "x"}},
        headers = auth_headers
    )
    assert create.status_code == 201, create.text
    module_id = create.json()["id"]

    resp = await client.patch(
        f"/api/modules/{module_id}",
        json = {"title": 37, "description": ["bad"]},
        headers = auth_headers
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_module_success_admin(client: AsyncClient, auth_headers):
    """Admin can PATCH /api/modules/{id} and update title and description"""
    create = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "test3", "description": "x"}},
        headers = auth_headers
    )
    assert create.status_code == 201, create.text
    module_id = create.json()["id"]

    resp = await client.patch(
        f"/api/modules/{module_id}",
        json = {"module_data": {"title": "Updated", "description": ""}},
        headers = auth_headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert_module_shape(data)
    assert data["title"] == "Updated"
    assert data["description"] is None


@pytest.mark.asyncio
async def test_update_module_not_found_admin(client: AsyncClient, auth_headers):
    """"Test that PATCH /api/modules/{id} returns 404 for non existent module"""
    resp = await client.patch(
        "/api/modules/123456",
        json = {"module_data": {"title": "Updated"}},
        headers = auth_headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_module_string_id_422(client: AsyncClient, auth_headers):
    """PATCH /api/modules/{id} returns 422 for invalid id type"""
    resp = await client.patch(
        "/api/modules/invalid",
        json = {"module_data": {"title": "Updated"}},
        headers = auth_headers,
    )
    assert resp.status_code == 422


#DELETE /api/modules/{id} (delete module)


@pytest.mark.asyncio
async def test_delete_module_requires_auth(client: AsyncClient):
    """DELETE /api/modules/{id} requires authentication"""
    resp = await client.delete("/api/modules/1")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_module_forbidden_for_non_admin(client: AsyncClient, auth_headers, user_headers):
    """Regular user can't DELETE /api/modules/{id}"""
    create = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "DeleteTarget", "description": "x"}},
        headers = auth_headers
    )
    assert create.status_code == 201, create.text
    module_id = create.json()["id"]

    resp = await client.delete(
        f"/api/modules/{module_id}",
        headers = user_headers
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_module_not_found(client: AsyncClient, auth_headers):
    """DELETE /api/modules/{id} returns 404 for non existent module"""
    resp = await client.delete("/api/modules/123456", headers = auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_module_success_admin(client: AsyncClient, auth_headers, user_headers):
    """Admin can DELETE /api/modules/{id} and then GET returns 404"""
    create = await client.post(
        "/api/modules",
        json = {"module_data": {"title": "Delete", "description": None}},
        headers = auth_headers
    )
    assert create.status_code == 201, create.text
    module_id = create.json()["id"]

    resp = await client.delete(
        f"/api/modules/{module_id}",
        headers = auth_headers
    )
    assert resp.status_code == 204
    assert resp.text == ""

    get_resp = await client.get(
        f"/api/modules/{module_id}", 
        headers = user_headers
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_module_string_id_422(client: AsyncClient, auth_headers):
    """Test that DELETE /api/modules/{id} returns 422 for invalid id type"""
    resp = await client.delete("/api/modules/invalid", headers = auth_headers)
    assert resp.status_code == 422
