import src.app as app_module
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Art Club": {
                "description": "Make art",
                "schedule": "Fridays",
                "max_participants": 10,
                "participants": ["existing@school.edu"],
            }
        },
    )
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Art Club"]["participants"] == ["existing@school.edu"]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "new@school.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@school.edu for Art Club"}
    assert client.get("/activities").json()["Art Club"]["participants"] == [
        "existing@school.edu",
        "new@school.edu",
    ]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "new@school.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Art%20Club/signup",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@school.edu from Art Club"
    }
    assert client.get("/activities").json()["Art Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "new@school.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Art%20Club/signup",
        params={"email": "unknown@school.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
