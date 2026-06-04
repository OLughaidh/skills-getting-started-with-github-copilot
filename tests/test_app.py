"""AAA-structured FastAPI backend tests for the activity API."""

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    """Provide a FastAPI test client for each test."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset the in-memory activities store before and after each test."""
    original = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"][:],
        }
        for name, activity in activities.items()
    }

    yield

    activities.clear()
    activities.update(original)


class TestGetActivities:
    def test_get_activities_returns_200(self, client, reset_activities):
        # Arrange
        # A valid FastAPI test client is available.

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data


class TestSignupFlow:
    def test_signup_adds_student_to_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert email in activities[activity_name]["participants"]

    def test_duplicate_signup_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "activity not found" in response.json()["detail"].lower()


class TestUnregisterFlow:
    def test_unregister_removes_participant(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "not-a-participant@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "participant not found" in response.json()["detail"].lower()
