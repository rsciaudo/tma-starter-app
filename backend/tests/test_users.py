"""
Contract-level tests for the /api/users endpoint
"""

import pytest
from httpx import AsyncClient


# -------------------
# Test GET /api/users
# -------------------
@pytest.mark.asyncio
async def test_get_all_users_requires_auth(client: AsyncClient):
    """Test that GET /api/users requires authentication"""
    response = await client.get("/api/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_users_with_auth(client: AsyncClient, auth_headers, admin_user):
    """Test that GET /api/users returns list of users when authenticated"""
    response = await client.get("/api/users", headers=auth_headers)
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


# End ----------------


# ------------------------
# Test GET /api/users/{id}
# ------------------------
@pytest.mark.asyncio
async def test_get_user_by_id_requires_auth(client: AsyncClient, user_auth_headers):
    """Test that GET /api/users/{id} requires authentication"""
    response = await client.get("/api/users/1")
    assert response.status_code == 401

    # test with headers that only have user access not admin
    response = await client.get("/api/users/1", headers=user_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that GET /api/users/{id} returns 404 for non-existent user"""
    response = await client.get("/api/users/99999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_by_id_incorrect_type_fields(client: AsyncClient, auth_headers):
    """Test that GET /api/users/{id} returns 422 for non-int required id input"""
    response = await client.get("/api/users/eleven", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_by_id_success(client: AsyncClient, auth_headers):
    """Test that GET /api/users/{id} returns 200 if a user matching the
    id is found, has all expected fields, and doesn't return the user's password"""
    response = await client.get("/api/users/1", headers=auth_headers)
    assert response.status_code == 200
    user = response.json()

    assert "id" in user
    assert "role" in user
    assert "email_verified" in user
    assert "is_active" in user
    assert "created_at" in user
    assert "updated_at" in user

    assert "password" not in user


# End ---------------


# --------------------
# Test POST /api/users
# --------------------
@pytest.mark.asyncio
async def test_create_user_requires_auth(client: AsyncClient, user_auth_headers):
    """Test that POST /api/users requires authentication"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    response = await client.post("/api/users", json=user_data)
    assert response.status_code == 401

    response = await client.post(
        "/api/users", json=user_data, headers=user_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, auth_headers, test_db):
    """Test that POST /api/users creates a user successfully"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "user",
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    # Password should not be in response

    # Verify the user was actually created by retrieving it through the API
    user_id = data["id"]
    get_response = await client.get(f"/api/users/{user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_user = get_response.json()
    assert retrieved_user["username"] == "newuser"
    assert retrieved_user["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_create_user_missing_fields(client: AsyncClient, auth_headers):
    """Test that POST /api/users returns 422 for missing required fields"""
    user_data = {
        "username": "testuser"
        # Missing email and password
    }
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_duplicate_username(
    client: AsyncClient, auth_headers, test_db
):
    """Test that POST /api/users returns error for duplicate username"""
    user_data = {
        "username": "duplicate",
        "email": "first@example.com",
        "password": "password123",
        "role": "user",
    }
    # Create first user
    create_response = await client.post(
        "/api/users", json=user_data, headers=auth_headers
    )
    assert create_response.status_code == 201
    first_user_id = create_response.json()["id"]

    # Verify the first user was actually created
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "duplicate"

    # Try to create duplicate username (different email)
    user_data["email"] = "second@example.com"
    response = await client.post("/api/users", json=user_data, headers=auth_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

    # Verify the first user still exists and wasn't affected
    get_response = await client.get(f"/api/users/{first_user_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert (
        get_response.json()["email"] == "first@example.com"
    )  # Original email unchanged


# End ------------------------


# --------------------------
# Test PATCH /api/users/{id}
# --------------------------
# TODO: Modify endpoint to allow a user to update PARTS of their own profile
# TODO: Make tests to verify this part
# TODO: about how a manager would recognize a user if they change their name...
# @Dr. Sarah. We discussed wanting the user to also be able to update some of their
# information. This would require modifying the endpoint/dependencies. I haven't done
# any implementation or testing, but I wanted to make a not of it
@pytest.mark.asyncio
async def test_patch_user_by_id_requires_auth(client: AsyncClient, user_auth_headers):
    """Test that PATCH /api/users/{id} requires authentication"""
    profile_data = {
        "first_name": "updatedFirstName",
    }
    response = await client.patch("/api/users/1", json=profile_data)
    assert response.status_code == 401

    response = await client.patch(
        "/api/users/1", json=profile_data, headers=user_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patch_user_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 404 for non-existent user"""
    profile_data = {
        "first_name": "updatedFirstName",
    }
    response = await client.patch(
        "/api/users/999999", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_user_by_id_not_int(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 422 for invalid id"""
    profile_data = {
        "first_name": "updatedFirstName",
    }
    response = await client.patch(
        "/api/users/eleven", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_by_id_empty_params_success(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} succeeds when given empty parameters,
    because all params are optional"""
    # First get the og user data
    response = await client.get("/api/users/1", headers=auth_headers)
    assert response.status_code == 200
    original_user_data = response.json()

    profile_data = {}
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200

    response = await client.get("/api/users/1", headers=auth_headers)
    assert response.status_code == 200
    new_user_data = response.json()
    assert new_user_data == original_user_data


@pytest.mark.asyncio
async def test_patch_user_by_id_no_params_given(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 422 because no paremeters were given"""
    response = await client.patch("/api/users/1", headers=auth_headers)
    assert response.status_code == 422


# @Dr. Sarah -- PATCH /api/users/{id} - int won't convert to String. Passing 391
# causes a 422 error. See the tagged issue for more detail
@pytest.mark.asyncio
async def test_patch_user_by_id_bad_params_given(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 422 for invalid parameter types"""
    # Most params are strings. They are not automatically converted to string.
    profile_data = {"first_name": 391}
    # NOTE: It is interesting that this one won't go through, but other
    # type conversions (checked in PATCH /api/users/{id}/status) go through just fine
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 422

    # Give a bad/un-convertable date value, which should cause 422 error
    profile_data = {"child_dob": "BAD DATE THERES NO WAY THIS CONVERTS"}
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_by_id_empty_string_param(client: AsyncClient, auth_headers):
    """ "Test that PATCH /api/users/{id}"""
    profile_data = {
        "first_name": "",
        "last_name": "",
        "child_name": "",
        "child_sex_assigned_at_birth": "",
        # "child_dob": "",
        # # DOB excluded because it will be a type error, and won't
        # allow me to test for empty string
        "avatar_url": "",
    }
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200

    response = await client.get("/api/users/1", headers=auth_headers)
    user_data = response.json()
    assert (
        user_data["first_name"] is None
    )  # How interesting, it get's saved as None, not ""
    # @Dr. Sarah ^^ This may be something to look at, but I don't really see it
    # as a particularly big deal


@pytest.mark.asyncio
async def test_patch_user_by_id_all_fields_success(client: AsyncClient, auth_headers):
    """Test that PATCH /api/users/{id} returns 200 for successful
    update of all fields and that the update persists, and that the updated_at
    time is actually changed"""
    # Get previous data for user to store for comparisson
    response = await client.get("/api/users/1", headers=auth_headers)
    original_user_data = response.json()

    profile_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "child_name": "UpdatedChildName",
        "child_sex_assigned_at_birth": "UpdatedChildSexAssignedAtBirth",
        "child_dob": "2026-01-29",
        "avatar_url": "UpdatedURL",
    }
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200  # Check the error code
    # Then re-retrieve the data to validated it persisted in the DB
    response = await client.get("/api/users/1", headers=auth_headers)
    updated_user_data = response.json()

    # Compare each value
    assert (
        original_user_data["first_name"] != updated_user_data["first_name"]
        and updated_user_data["first_name"] == profile_data["first_name"]
    )
    assert (
        original_user_data["last_name"] != updated_user_data["last_name"]
        and updated_user_data["last_name"] == profile_data["last_name"]
    )
    assert (
        original_user_data["child_name"] != updated_user_data["child_name"]
        and updated_user_data["child_name"] == profile_data["child_name"]
    )
    assert (
        original_user_data["child_sex_assigned_at_birth"]
        != updated_user_data["child_sex_assigned_at_birth"]
        and updated_user_data["child_sex_assigned_at_birth"]
        == profile_data["child_sex_assigned_at_birth"]
    )
    assert (
        original_user_data["child_dob"] != updated_user_data["child_dob"]
        and updated_user_data["child_dob"] == profile_data["child_dob"]
    )
    assert (
        original_user_data["avatar_url"] != updated_user_data["avatar_url"]
        and updated_user_data["avatar_url"] == profile_data["avatar_url"]
    )

    # Also check that the updated time is updated
    assert original_user_data["created_at"] == updated_user_data["created_at"]
    assert original_user_data["updated_at"] < updated_user_data["updated_at"]


@pytest.mark.asyncio
async def test_patch_user_by_id_partial_fields_success(
    client: AsyncClient, auth_headers
):
    """Test that PATCH /api/users/{id} returns 200 for successful update
    which changes some of the fields and that the update persists"""
    # Get previous data for user to store for comparisson
    response = await client.get("/api/users/1", headers=auth_headers)
    original_user_data = response.json()

    profile_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        # Only update some of the fields
        "CHILDNAME": "Shouldn't be seen",
    }
    response = await client.patch(
        "/api/users/1", headers=auth_headers, json=profile_data
    )
    assert response.status_code == 200  # Check the error code
    # Then re-retrieve the data to validated it persisted in the DB
    response = await client.get("/api/users/1", headers=auth_headers)
    updated_user_data = response.json()

    # First and last name should be updated, and should be different
    # from the original values
    assert (
        original_user_data["first_name"] != updated_user_data["first_name"]
        and updated_user_data["first_name"] == profile_data["first_name"]
    )
    assert (
        original_user_data["last_name"] != updated_user_data["last_name"]
        and updated_user_data["last_name"] == profile_data["last_name"]
    )

    # The rest should not have been updated
    assert original_user_data["child_name"] == updated_user_data["child_name"]
    assert (
        original_user_data["child_sex_assigned_at_birth"]
        == updated_user_data["child_sex_assigned_at_birth"]
    )
    assert original_user_data["child_dob"] == updated_user_data["child_dob"]
    assert original_user_data["avatar_url"] == updated_user_data["avatar_url"]

    assert "CHILDNAME" not in updated_user_data


# End ------------------------


# --------------------------
# Test DELETE /api/users/{id}
# --------------------------
@pytest.mark.asyncio
async def test_delete_user_by_id_requires_auth(client: AsyncClient, user_auth_headers):
    """Test that DELETE /api/users/{id} requires authentication"""
    response = await client.delete(
        "/api/users/1",
    )
    assert response.status_code == 401

    response = await client.delete("/api/users/1", headers=user_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_by_id_not_found(client: AsyncClient, auth_headers):
    """Test that DELETE /api/users/{id} returns 404 for non-existent user"""
    response = await client.delete("/api/users/99999999999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_by_id_incorrect_type_fields(
    client: AsyncClient, auth_headers
):
    """Test that DELETE /api/users/{id} returns 422 because
    invalid paremeters were given"""
    response = await client.delete("/api/users/eleven", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_user_by_id_prevent_delete_self(
    client: AsyncClient, auth_headers, admin_user
):
    """Test that DELETE /api/users/{id} returns 400 if you try to delete yourself"""

    response = await client.delete(f"/api/users/{admin_user.id}", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_by_id_successful(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that DELETE /api/users/{id} returns 204 when a user is
    deleted and that it persists"""

    id_to_delete = regular_user.id
    # Confirm that the user exists before deletion
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 200

    # I checked above, the admin user is id = 1, so  I can't
    # delete that one. Deleting new user instead
    response = await client.delete(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 204  # Verify the deletion code

    with pytest.raises(
        ValueError
    ):  # Checks if trying to get the json of the response would
        response.json()  # raise an error, which it should
    # Then verify that it's actually gone
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_by_id_prevent_double_delete(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that DELETE /api/users/{id} returns 404 when trying to delete a
    user for the second time"""
    id_to_delete = regular_user.id
    # Confirm that the new user exists before deletion
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 200

    # I checked above, the admin user is id = 1, so  I can't
    # delete that one. Deleting new user instead
    response = await client.delete(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 204  # Verify the deletion code

    # Then try the deletion again
    response = await client.delete(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_by_id_inactive_account(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that DELETE /api/users/{id} returns 200 when deleting an inactive account"""
    id_to_delete = regular_user.id
    change_status = {"user_id": id_to_delete, "is_active": False}
    response = await client.patch(
        f"/api/users/{id_to_delete}/status", json=change_status, headers=auth_headers
    )
    assert response.status_code == 200  # Verify that the change went through
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.json()["is_active"] is False

    # Now delete them
    response = await client.delete(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 204

    # Verify they're gone
    response = await client.get(f"/api/users/{id_to_delete}", headers=auth_headers)
    assert response.status_code == 404


# End ------------------------


# ---------------------------------
# Test PATCH /api/users/{id}/status
# ---------------------------------
@pytest.mark.asyncio
async def test_patch_user_status_by_id_requires_auth(
    client: AsyncClient, user_auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status requires authentication"""
    status_data = {"user_id": regular_user.id, "is_active": False}
    response = await client.patch("/api/users/regular_user.id/status", json=status_data)
    assert response.status_code == 401

    response = await client.patch(
        "/api/users/regular_user.id/status", json=status_data, headers=user_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patch_user_status_by_id_not_found(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status returns 404 for non-existent user"""
    status_data = {"user_id": regular_user.id, "is_active": False}
    response = await client.patch(
        "/api/users/999999/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_user_status_by_id_not_int(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status returns 422 for invalid id in the URL"""
    status_data = {"user_id": regular_user.id, "is_active": False}
    response = await client.patch(
        "/api/users/eleven/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_status_by_id_no_parameters(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status returns 422 because
    no paremeters were given"""
    id_to_use = regular_user.id

    response = await client.patch(
        f"/api/users/{id_to_use}/status", headers=auth_headers
    )
    assert response.status_code == 422


# @Dr. Sarah, this one isn't super important, but it's good to note that
# a lot of the behavior is as we'd expect
@pytest.mark.asyncio
async def test_patch_user_status_by_id_bad_parameters(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status returns 422 for invalid
    parameter types and empty parameters"""
    id_to_use = regular_user.id

    # Empty params
    status_data = {}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422

    # Empty String params
    status_data = {"user_id": "", "is_active": False}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422

    status_data = {"user_id": 55, "is_active": ""}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422

    # Bad type for user_id
    status_data = {"user_id": "eleven", "is_active": False}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422

    # Bad type for is_active
    status_data = {"user_id": 55, "is_active": "dkgbdsflkjb"}
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 422


# @Dr. Sarah. -- PATCH /api/users/{id}/status - some 'int' and 'String' will convert
# to 'boolean'
# This is the function with the boolean we were talking about in class. See the issue
# I attached to the PR for more discussion on it.
@pytest.mark.asyncio
async def test_patch_user_status_by_id_convertable_parameters(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status returns 200 for parameters
    where the types can be converted"""
    id_to_use = regular_user.id

    # True = 1 False  = 0
    # Get the user and verify their status is active?
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200
    original_user_data = response.json()
    assert original_user_data["is_active"] is True

    # Permissible type for user_id
    # The reason this is possible is because it's not actually reading the user_id from
    # the parameter, it's looking at the id passed into the url (see next test for more
    # definitive proof)
    status_data = {
        "user_id": "2",
        "is_active": False,
    }  # Could just be ignoring the "2" for user
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 200
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200
    original_user_data = response.json()
    assert original_user_data["is_active"] is False  # It did actually change

    # Permissible type for is_active.
    # Also tests which ID is used if a different one
    # is passed in for the parameter and the url. In this case, it ignores the parameter
    # one, 55, and uses the one in the url, id_to_user, which is 2
    status_data = {"user_id": 55, "is_active": 1}
    response = await client.patch(
        f"/api/users/{id_to_use}/status",
        json=status_data,
        headers=auth_headers,
        # NOTE: It is ignoring the user_id parameter in the body, and only looking
        # at the user id in the url
    )
    assert response.status_code == 200
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200
    original_user_data = response.json()
    assert original_user_data["is_active"] is True  # It did actually change (again)

    status_data = {"user_id": 55, "is_active": "false"}
    response = await client.patch(
        f"/api/users/{id_to_use}/status",
        json=status_data,
        headers=auth_headers,
        # NOTE: It is ignoring the user_id parameter in the body, and only
        # looking at the  user id in the url
    )
    assert response.status_code == 200
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200
    original_user_data = response.json()
    assert original_user_data["is_active"] is False  # It did actually change (again)

    # NOTE: Interestingly, these bad parameters can convert, wherease the
    # first_name parameter of PATCH /api/users/{id} can't convert from int to string


@pytest.mark.asyncio
async def test_patch_user_status_by_id_prevent_disable_self(
    client: AsyncClient, auth_headers, admin_user
):
    """Test that PATCH /api/users/{id}/status returns 400 if you try
    to disable yourself"""
    status_data = {"user_id": admin_user.id, "is_active": False}
    response = await client.patch(
        f"/api/users/{admin_user.id}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_user_status_by_id_successful(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/status returns 200 for successful
    status update and that the update persists"""
    # Add a second user to the DB to test with a correct URL
    id_to_use = regular_user.id

    # Get the original info for later comparison
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200  # Make sure it was made
    original_data = response.json()

    # Actual test
    status_data = {
        "user_id": id_to_use,
        "is_active": not original_data[
            "is_active"
        ],  # Negate the original activity status
    }
    response = await client.patch(
        f"/api/users/{id_to_use}/status", json=status_data, headers=auth_headers
    )
    assert response.status_code == 200  # Confirm the code
    response_data = response.json()

    # Check that the user is returned
    assert (
        "id" in response_data
        and "role" in response_data
        and "email_verified" in response_data
        and "is_active" in response_data
        and "created_at" in response_data
        and "updated_at" in response_data
    )

    # Then check the user's updated info persisted
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    updated_data = response.json()

    assert (
        original_data["is_active"] != updated_data["is_active"]
    )  # Check that they're opposites


# End ----------------------


# ---------------------------------
# Test PATCH /api/users/{id}/role
# ---------------------------------
@pytest.mark.asyncio
async def test_patch_user_role_by_id_requires_auth(
    client: AsyncClient, user_auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role requires authentication"""
    role_data = {"user_id": regular_user.id, "role": "manager"}
    response = await client.patch(f"/api/users/{regular_user.id}/role", json=role_data)
    assert response.status_code == 401

    response = await client.patch(
        f"/api/users/{regular_user.id}/role", json=role_data, headers=user_auth_headers
    )
    assert (
        response.status_code == 403
    )  # Should fail because a regular user doesn't have permission to do this


@pytest.mark.asyncio
async def test_patch_user_role_by_id_not_found(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role returns 404 for non-existent user"""
    role_data = {"user_id": regular_user.id, "role": "manager"}
    response = await client.patch(
        "/api/users/999999/role", json=role_data, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_user_role_by_id_not_int(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role returns 422 for invalid
    id in the URL"""
    role_data = {"user_id": regular_user.id, "role": "manager"}
    response = await client.patch(
        "/api/users/eleven/role", json=role_data, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_role_by_id_no_parameters(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role returns 422 because no
    paremeters were given"""
    id_to_use = regular_user.id

    response = await client.patch(f"/api/users/{id_to_use}/role", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_role_by_id_bad_parameters(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role returns 422 for invalid
    parameter types and empty parameters"""
    id_to_use = regular_user.id

    # Empty params
    role_data = {}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422

    # Empty Strings
    role_data = {"user_id": "", "role": "manager"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422
    # empty role is handled in the _invalid_role function

    # bad type for user_id
    role_data = {"user_id": "eleven", "role": "manager"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422

    # bad type for role, as in integer etc
    role_data = {"user_id": id_to_use, "role": 7983298}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_user_role_by_id_invalid_role(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role returns 400 for invalid role given"""
    id_to_use = regular_user.id

    # Actual test
    role_data = {"user_id": id_to_use, "role": "notAdmin"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 400

    role_data = {"user_id": id_to_use, "role": ""}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_user_role_by_id_convertable_parameters(
    client: AsyncClient, auth_headers, regular_user
):
    """Test that PATCH /api/users/{id}/role returns 200 for parameters
    where the types can be converted"""
    id_to_use = regular_user.id

    # Permissible type for user_id
    role_data = {"user_id": id_to_use, "role": "manager"}
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_user_role_by_id_prevent_change_own_role(
    client: AsyncClient, auth_headers, admin_user
):
    """Test that PATCH /api/users/{id}/role returns 400 if you
    try to change your role"""
    role_data = {"user_id": admin_user.id, "role": "user"}
    response = await client.patch(
        f"/api/users/{admin_user.id}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_user_role_to_manager_by_id_successful(
    client: AsyncClient, auth_headers, regular_user, user_auth_headers
):
    """Test that PATCH /api/users/{id}/status returns 200 for
    successful status update and that the update persists"""
    id_to_use = regular_user.id

    # Get the original info for later comparison
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200  # Make sure it was made
    original_data = response.json()

    role_data = {
        "user_id": id_to_use,
        "role": "manager",  # New role from the original one set
    }
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 200
    response_data = response.json()

    # Check that the user is returned
    assert (
        "id" in response_data
        and "role" in response_data
        and "email_verified" in response_data
        and "is_active" in response_data
        and "created_at" in response_data
        and "updated_at" in response_data
    )

    # Then check that the updated info has persisted
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    updated_data = response.json()
    assert (
        original_data["role"] != updated_data["role"]
        and updated_data["role"]["name"] == "manager"
    )

    # Test they can now make calls to things like GET /api/users/{id}
    response = await client.get("/api/users/1", headers=user_auth_headers)
    assert response.status_code == 403  # I guess managers can make this call


@pytest.mark.asyncio
async def test_patch_user_role_to_admin_by_id_successful(
    client: AsyncClient, auth_headers, regular_user, user_auth_headers
):
    """Test that PATCH /api/users/{id}/status returns 200 for
    successful status update and that the update persists"""
    id_to_use = regular_user.id

    # Get the original info for later comparison
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    assert response.status_code == 200  # Make sure it was made
    original_data = response.json()

    role_data = {
        "user_id": id_to_use,
        "role": "admin",
    }
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 200
    response_data = response.json()

    # Check that the user is returned
    assert (
        "id" in response_data
        and "role" in response_data
        and "email_verified" in response_data
        and "is_active" in response_data
        and "created_at" in response_data
        and "updated_at" in response_data
    )

    # Then check that the updated info has persisted
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    updated_data = response.json()
    assert (
        original_data["role"] != updated_data["role"]
        and updated_data["role"]["name"] == "admin"
    )

    # Test they can now make calls to things like GET /api/users/{id}
    response = await client.get("/api/users/1", headers=user_auth_headers)
    assert response.status_code == 200


# @Dr. Sarah -- Fixtures Issue
# The comments try to explain it, but basically once the regular_user is promoted
# The user_auth_header *does* get upgraded to represent the fact that it's now an
# admin (verified by trying to GET a protected route). But somehow the fixture
# makes the two auth_headers come across as the SAME auth_header. Essentially,
# it causes all admins to be seen as the same admin, so the endpoint rejects it
# because you're not supposed to be able to demote yourself.


@pytest.mark.asyncio
async def test_patch_user_role_to_admin_then_demote_another_admin(
    client: AsyncClient, admin_user, auth_headers, regular_user, user_auth_headers
):
    """Test that PATCH /api/users/{id}/status returns 200 for
    successful status update and that they can then demote other admins"""
    id_to_use = regular_user.id

    role_data = {
        "user_id": id_to_use,
        "role": "admin",
    }
    response = await client.patch(
        f"/api/users/{id_to_use}/role", headers=auth_headers, json=role_data
    )
    assert response.status_code == 200

    # Then check that the updated info has persisted
    response = await client.get(f"/api/users/{id_to_use}", headers=auth_headers)
    updated_data = response.json()
    assert updated_data["role"]["name"] == "admin"

    # Test they can now make calls to things like GET /api/users/{id}
    # Repeat test as last function as sanity check
    # (the user_auth_headers now has admin powers)
    response = await client.get("/api/users/1", headers=user_auth_headers)
    assert response.status_code == 200

    # Additional proof that the endpoint is seeing the two auth headers fixtures
    # as the same object (which is the reason the call after fails)

    assert auth_headers != user_auth_headers  # <-- currently failing

    # Now see if the new admin (regular_user, user_auth_headers) can
    # demote the original admin (admin_user, auth_headers)
    role_data = {"user_id": admin_user.id, "role": "user"}
    response = await client.patch(
        f"/api/users/{admin_user.id}/role", headers=user_auth_headers, json=role_data
    )  # pass in the id of the original admin, and use the headers
    # credentials of the new admin
    assert response.status_code == 200  # <-- Currently fails (400 error) because it
    # thinks the admin is trying to demote themselves
