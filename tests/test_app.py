from fastapi.testclient import TestClient
from src.app import activities, app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_new_participant_and_restores_state():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest_new_student@example.com"
    signup_url = f"/activities/{activity_name}/signup"
    delete_url = f"/activities/{activity_name}/participants"

    try:
        # Act
        signup_response = client.post(signup_url, params={"email": email})

        # Assert
        assert signup_response.status_code == 200
        assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    finally:
        # Restore state
        if email in activities[activity_name]["participants"]:
            client.delete(delete_url, params={"email": email})


def test_signup_for_activity_returns_error_for_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    existing_student_email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": existing_student_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_student_from_activity():
    # Arrange
    activity_name = "Soccer Club"
    email = "pytest_unregister_student@example.com"
    signup_url = f"/activities/{activity_name}/signup"
    delete_url = f"/activities/{activity_name}/participants"

    try:
        signup_response = client.post(signup_url, params={"email": email})
        assert signup_response.status_code == 200

        # Act
        delete_response = client.delete(delete_url, params={"email": email})

        # Assert
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
    finally:
        if email in activities[activity_name]["participants"]:
            client.delete(delete_url, params={"email": email})


def test_unregister_participant_returns_error_when_student_not_signed_up():
    # Arrange
    activity_name = "Soccer Club"
    email = "pytest_nonexistent_student@example.com"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up"
