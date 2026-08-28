import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app_clinician import app, generate_task_id


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_generate_task_id():
    # Test task ID generation and duplicate prevention
    dummy_tasks = {"task001": {}, "task002": {}}
    assert generate_task_id(dummy_tasks) == "task003"


def test_create_task_validation(client):
    response = client.post(
        "/clinician/create_task",  # Changed from hyphen to underscore
        data={"title": "", "description": "", "due_date": ""},
    )
    assert response.status_code == 302


def test_review_submission_valid(client):
    # Test valid review outcome submission
    response = client.post(
        "/clinician/review/12342024_task001",
        data={
            "review_status": "Needs Follow-up",
            "notes": "Schedule a call with patient.",
        },
    )
    assert response.status_code == 302


def test_review_submission_invalid(client):
    # Numerical grade should be rejected/redirected
    response = client.post(
        "/clinician/review/12342024_task001",
        data={"review_status": "95/100", "notes": "Great job"},
    )
    assert response.status_code == 302