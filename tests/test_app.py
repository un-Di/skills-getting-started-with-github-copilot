"""Test suite for FastAPI Mergington High School activities app."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


def test_get_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["max_participants"] == 12


def test_get_activities_structure(client):
    """Test that activity structure is correct"""
    response = client.get("/activities")
    data = response.json()
    activity = data["Chess Club"]
    
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    email = "test@mergington.edu"
    activity_name = "Tennis Club"
    
    # Get initial participant count
    response = client.get("/activities")
    initial_count = len(response.json()[activity_name]["participants"])
    
    # Sign up
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    new_count = len(response.json()[activity_name]["participants"])
    assert new_count == initial_count + 1
    assert email in response.json()[activity_name]["participants"]


def test_signup_already_registered(client):
    """Test signup fails when student is already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered for Chess Club
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_nonexistent_activity(client):
    """Test signup fails for nonexistent activity"""
    response = client.post(
        "/activities/Fake Activity/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_participant_success(client):
    """Test successful removal of a participant"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered
    
    # Verify participant exists
    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]
    
    # Remove participant
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_remove_nonexistent_participant(client):
    """Test removal fails for participant not in activity"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_from_nonexistent_activity(client):
    """Test removal fails for nonexistent activity"""
    response = client.delete(
        "/activities/Fake Activity/participants",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_and_remove_cycle(client):
    """Test full cycle of signup and removal"""
    activity_name = "Drama Club"
    email = "newstudent@mergington.edu"
    
    # Sign up
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify registered
    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]
    
    # Remove
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify removed
    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]
