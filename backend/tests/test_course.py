"""
Contract-level tests for the /api/courses endpoint
"""

import pytest
from httpx import AsyncClient


# helper function
def verify_original_course_info(original_course, create_course, key):
    return original_course[key] == getattr(create_course, key)


# get endpoint tests


@pytest.mark.asyncio
async def test_get_all_courses_auth(client: AsyncClient):
    """Test that GET /api/courses requires authentication"""
    response = await client.get("/api/courses")
    assert response.status_code == 401


# split auth_headers into
@pytest.mark.asyncio
async def test_get_all_courses_with_admin_auth(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test GET /api/courses with admin role while authenticated"""
    response = await client.get(
        "/api/courses",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # verify the list contains at least 1 course
    assert len(data) >= 1

    # verify the created course contains the required fields
    for course in data:
        assert "id" in course
        assert "title" in course
        assert "description" in course
        assert "created_at" in course
        assert "updated_at" in course
        assert "module_count" in course


@pytest.mark.asyncio
async def test_get_all_us_courses_with_no_admin_auth(
    client: AsyncClient, user_auth_headers
):
    """Test GET /api/courses without admin role while authenticated"""
    response = await client.get(
        "/api/courses",
        headers=user_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # verify the list contains no courses bc lack of auth
    assert data == []


@pytest.mark.asyncio
async def test_get_course_by_id_requires_auth(client: AsyncClient, create_course):
    """Test GET /api/courses/{course_id} without authentication"""
    response = await client.get(f"/api/courses/{create_course.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_course_by_valid_id(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test GET /api/courses/{course_id} while authenticated"""
    response = await client.get(
        f"/api/courses/{create_course.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # verify the data is returned as a dict
    assert isinstance(data, dict)

    # verify the created course contains the required fields
    # and the fields are correct for the specific course

    assert data["id"] == create_course.id
    assert data["title"] == create_course.title
    assert data["description"] == create_course.description
    assert data["modules"] == []
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_course_by_invalid_id(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test GET /api/courses/{course_id} while authenticated"""
    response = await client.get(
        "/api/courses/0",
        headers=auth_headers,
    )
    # test if error code thrown by endpoint is the one expected
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_course_by_invalid_identifier(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test GET /api/courses/{course_id} with invalid identifier"""
    response = await client.get(
        "/api/courses/abcdefg",
        headers=auth_headers,
    )
    # test if error code thrown by endpoint is the one expected
    assert response.status_code == 422


# post endpoint tests


@pytest.mark.asyncio
async def test_create_course_requires_auth(client: AsyncClient):
    """Test POST /api/courses requires auth"""
    course_data = {"title": "test_course"}
    response = await client.post("/api/courses", json=course_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_course_authenticated_but_not_admin(
    client: AsyncClient, user_auth_headers
):
    """Test POST /api/courses rejects authenticated non-admin users"""
    course_data = {"title": "non_admin_course", "description": "dont allow this thanks"}
    response = await client.post(
        "/api/courses",
        json=course_data,
        headers=user_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_course_valid_input(client: AsyncClient, auth_headers, admin_user):
    """Test POST /api/courses with valid input"""
    course_data = {"title": "test_course", "description": "Test course description"}
    response = await client.post("/api/courses", json=course_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    # test that returned data contains all expected fields
    assert data["title"] == "test_course"
    assert data["description"] == "Test course description"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # test if the data was actually saved
    course_id = data["id"]
    get_response = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get_response.status_code == 200
    returned_course = get_response.json()
    assert returned_course["title"] == "test_course"
    assert returned_course["description"] == "Test course description"


@pytest.mark.asyncio
async def test_create_course_missing_fields(client: AsyncClient, auth_headers):
    """Test that POST /api/courses returns 422 for missing required fields"""
    user_data = {
        "description": "nope"
        # Missing title and
    }
    response = await client.post("/api/courses", json=user_data, headers=auth_headers)
    assert response.status_code == 422


# make endpoint not accept empty strings for titles


# patch endpoint tests


@pytest.mark.asyncio
async def test_patch_course_requires_auth(client: AsyncClient, create_course):
    """Test PATCH /api/courses/{course_id} requires auth"""
    course_data = {"title": "test_course"}
    response = await client.patch(f"/api/courses/{create_course.id}", json=course_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_course_authenticated_but_not_admin(
    client: AsyncClient, user_auth_headers, create_course
):
    """Test PATCH /api/courses/{course_id} rejects authenticated non-admin users"""
    course_data = {
        "title": "non_admin_course",
    }
    response = await client.patch(
        f"/api/courses/{create_course.id}",
        json=course_data,
        headers=user_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patch_course_title_and_desc(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test PATCH /api/courses/{course_id} with valid input"""
    # test that name is already "Test Course", and desc already "A course for testing"
    get_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    original_course = get_response.json()
    assert verify_original_course_info(original_course, create_course, "title")
    assert verify_original_course_info(original_course, create_course, "description")

    course_data = {
        "title": "changed_test_course",
        "description": "Test course description",
    }
    response = await client.patch(
        f"/api/courses/{create_course.id}", json=course_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # test that returned data contains expected fields that are correct
    assert data["title"] == "changed_test_course"
    assert data["description"] == "Test course description"

    # test if the data was actually saved
    course_id = data["id"]
    get2_response = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get2_response.status_code == 200
    returned_course = get2_response.json()
    assert returned_course["title"] == "changed_test_course"
    assert returned_course["description"] == "Test course description"


@pytest.mark.asyncio
async def test_patch_course_title_only(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test PATCH /api/courses/{course_id} with only title"""
    # test that name is already "Test Course", and desc already "A course for testing"
    get1_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    original_course = get1_response.json()
    assert verify_original_course_info(original_course, create_course, "title")
    assert verify_original_course_info(original_course, create_course, "description")

    course_data = {
        "title": "changed_test_course",
    }
    response = await client.patch(
        f"/api/courses/{create_course.id}", json=course_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # test that returned data contains expected fields that are correct
    assert data["title"] == "changed_test_course"
    assert data["description"] == "A course for testing"

    # test if the data was actually saved
    course_id = data["id"]
    get2_response = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get2_response.status_code == 200
    returned_course = get2_response.json()
    assert returned_course["title"] == "changed_test_course"
    assert returned_course["description"] == "A course for testing"


@pytest.mark.asyncio
async def test_patch_course_desc_only(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test PATCH /api/courses/{course_id} with only description"""
    # test that name is already "Test Course", and desc already "A course for testing"
    get1_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    original_course = get1_response.json()
    assert verify_original_course_info(original_course, create_course, "title")
    assert verify_original_course_info(original_course, create_course, "description")

    course_data = {"description": "Test course description"}
    response = await client.patch(
        f"/api/courses/{create_course.id}", json=course_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # test that returned data contains expected fields that are correct
    assert data["title"] == "Test Course"
    assert data["description"] == "Test course description"

    # test if the data was actually saved
    course_id = data["id"]
    get2_response = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get2_response.status_code == 200
    returned_course = get2_response.json()
    assert returned_course["title"] == "Test Course"
    assert returned_course["description"] == "Test course description"


@pytest.mark.asyncio
async def test_patch_course_no_data(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test PATCH /api/courses/{course_id} with no data"""
    # test that name is already "Test Course", and desc already "A course for testing"
    get1_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    original_course = get1_response.json()
    assert verify_original_course_info(original_course, create_course, "title")
    assert verify_original_course_info(original_course, create_course, "description")

    course_data = {}
    response = await client.patch(
        f"/api/courses/{create_course.id}", json=course_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # test that returned data contains expected fields that are correct
    assert data["title"] == "Test Course"
    assert data["description"] == "A course for testing"

    # test if the data was actually saved
    course_id = data["id"]
    get2_response = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get2_response.status_code == 200
    returned_course = get2_response.json()
    assert verify_original_course_info(returned_course, create_course, "title")
    assert verify_original_course_info(returned_course, create_course, "description")


# ask about this
@pytest.mark.asyncio
async def test_patch_course_empty_title(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test PATCH /api/courses/{course_id} with valid input"""
    # test that name is already "Test Course", and desc already "A course for testing"
    get1_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    original_course = get1_response.json()
    assert verify_original_course_info(original_course, create_course, "title")
    assert verify_original_course_info(original_course, create_course, "description")

    course_data = {
        "title": "",
        "description": "Test course description",
    }
    response = await client.patch(
        f"/api/courses/{create_course.id}", json=course_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # test that returned data contains expected fields that are correct
    assert data["title"] == ""
    assert data["description"] == "Test course description"

    # test if the data was actually saved
    course_id = data["id"]
    get2_response = await client.get(f"/api/courses/{course_id}", headers=auth_headers)
    assert get2_response.status_code == 200
    returned_course = get2_response.json()
    assert returned_course["title"] == ""
    assert returned_course["description"] == "Test course description"


@pytest.mark.asyncio
async def test_patch_course_with_nonexistant_id(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test patch /api/courses/{course_id} with nonexistant id"""
    course_data = {
        "title": "changed_test_course",
        "description": "Test course description",
    }

    response = await client.patch(
        "/api/courses/0",
        json=course_data,
        headers=auth_headers,
    )
    # test if error code thrown by endpoint is the one expected
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_course_by_invalid_id(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test patch /api/courses/{course_id} with invalid id"""
    course_data = {
        "title": "changed_test_course",
        "description": "Test course description",
    }

    response = await client.patch(
        "/api/courses/abcdefg",
        json=course_data,
        headers=auth_headers,
    )
    # test if error code thrown by endpoint is the one expected
    assert response.status_code == 422


# ask if this is expected behavior or not
@pytest.mark.asyncio
async def test_patch_course_change_id(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test patch /api/courses/{course_id} changing id"""
    course_data = {
        "id": "100",
    }

    response = await client.patch(
        f"/api/courses/{create_course.id}",
        json=course_data,
        headers=auth_headers,
    )
    # test if error code thrown by endpoint is the one expected
    assert response.status_code == 200

    # test if the id can actually change
    response2 = await client.get(
        "/api/courses/1",  # 1 b/c thats whats the unchanged course id should be
        headers=auth_headers,
    )

    assert response2.json()["title"] == "Test Course"


@pytest.mark.asyncio
async def test_patch_course_with_invalid_body(
    client: AsyncClient, auth_headers, admin_user, create_course
):
    """Test patch /api/courses/{course_id} with invalid body"""
    course_data = {
        "title": 7,
        "description": ["hmm"],
    }

    response = await client.patch(
        f"/api/courses/{create_course.id}",
        json=course_data,
        headers=auth_headers,
    )
    # test if error code thrown by endpoint is the one expected
    assert response.status_code == 422

    # test if anything in the db was changed
    get1_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    original_course = get1_response.json()
    assert verify_original_course_info(original_course, create_course, "title")
    assert verify_original_course_info(original_course, create_course, "description")


# delete course tests


@pytest.mark.asyncio
async def test_delete_course_requires_auth(client: AsyncClient, create_course):
    """Test DELETE /api/courses/{course_id} requires auth"""
    response = await client.delete(f"/api/courses/{create_course.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_course_authenticated_but_not_admin(
    client: AsyncClient, user_auth_headers, create_course
):
    """Test DELETE /api/courses/{course_id} rejects authenticated non-admin users"""
    response = await client.delete(
        f"/api/courses/{create_course.id}",
        headers=user_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_course_valid(client: AsyncClient, auth_headers, create_course):
    """Test DELETE /api/courses/{course_id} with valid course & credentials"""
    # test that course with associated id actually exists
    get_response = await client.get(
        f"/api/courses/{create_course.id}", headers=auth_headers
    )
    assert get_response.status_code == 200

    # now delete it
    response = await client.delete(
        f"/api/courses/{create_course.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    # test that it was actually deleted
    response2 = await client.get(
        f"/api/courses/{create_course.id}",
        headers=auth_headers,
    )
    assert response2.status_code == 404


@pytest.mark.asyncio
async def test_delete_course_nonexistant_course_id(
    client: AsyncClient, auth_headers, create_course
):
    """Test DELETE /api/courses/{course_id} with nonexistant course"""
    response = await client.delete(
        "/api/courses/0",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_course_invalid_course_id(
    client: AsyncClient, auth_headers, create_course
):
    """Test DELETE /api/courses/{course_id} with bad course id"""
    response = await client.delete(
        "/api/courses/abcdefg",
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_course_twice(client: AsyncClient, auth_headers, create_course):
    """Test DELETE /api/courses/{course_id} with nonexistant course"""
    response = await client.delete(
        f"/api/courses/{create_course.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    response2 = await client.delete(
        f"/api/courses/{create_course.id}",
        headers=auth_headers,
    )
    assert response2.status_code == 404
