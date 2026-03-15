import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/static/index.html")


def test_get_activities_returns_data():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant():
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_same_student_twice_returns_400():
    email = "existing@mergington.edu"
    # First signup should work
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    assert response.status_code == 200

    # Second signup should fail
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_invalid_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert response.status_code == 404


def test_unregister_from_activity_removes_participant():
    email = "john@mergington.edu"
    response = client.delete(
        "/activities/Gym%20Class/participants", params={"email": email}
    )
    assert response.status_code == 200
    assert email not in activities["Gym Class"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Gym%20Class/participants", params={"email": "nobody@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_unregister_missing_activity_returns_404():
    response = client.delete(
        "/activities/NotAnActivity/participants", params={"email": "x@x.com"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
