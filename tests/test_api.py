import sys
from pathlib import Path

# Ensure `src` is on sys.path so tests can import the application module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from app import app, activities


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for an activity defined in the app
    assert "Chess Club" in data


def test_signup_and_unregister():
    client = TestClient(app)
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Unregister
    resp2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_duplicate_signup():
    client = TestClient(app)
    activity = "Chess Club"
    email = "dup.user@example.com"

    # Cleanup before test
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # First signup should work
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # Second signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Cleanup
    client.delete(f"/activities/{activity}/participants?email={email}")
