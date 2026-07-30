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
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200

    response = client.get("/activities")
    assert response.status_code == 200
    assert "test@example.com" in response.json()["Chess Club"]["participants"]


def test_unregister_existing_participant(client):
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200

    response = client.delete("/activities/Chess Club/unregister?email=test@example.com")
    assert response.status_code == 200
    assert "Removed test@example.com" in response.json()["message"]
    assert "test@example.com" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_missing_participant(client):
    response = client.delete("/activities/Chess Club/unregister?email=missing@example.com")
    assert response.status_code == 404
