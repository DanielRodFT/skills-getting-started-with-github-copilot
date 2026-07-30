from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


BASELINE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASELINE_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASELINE_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_signup_updates_activity_data(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    response = client.get("/activities")
    assert response.status_code == 200
    assert email in response.json()[activity_name]["participants"]


def test_unregister_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert f"Removed {email}" in response.json()["message"]
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
