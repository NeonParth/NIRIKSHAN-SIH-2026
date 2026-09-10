"""API tests require PostgreSQL/PostGIS via DATABASE_URL."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.models.enums import DataSource

RUN_DB = os.getenv("NIRIKSHAN_DB_TESTS") == "1" or bool(os.getenv("DATABASE_URL"))


@pytest.fixture(scope="module")
def client():
    if not RUN_DB:
        pytest.skip("DATABASE_URL not configured for API tests")
    from app.database.connection import database_connected, engine
    from app.main import app

    if not database_connected():
        pytest.skip("database is not reachable")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT PostGIS_Version()"))
    except Exception:
        pytest.skip("PostGIS is not available")
    return TestClient(app)


def test_health_connected(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"


def test_list_projects_provenance(client: TestClient):
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body and "total" in body
    if body["items"]:
        assert body["items"][0]["data_source"] in {item.value for item in DataSource}


def test_create_and_get_project(client: TestClient):
    code = f"TEST-{uuid4().hex[:8]}"
    created = client.post(
        "/api/v1/projects",
        json={
            "code": code,
            "name": "Synthetic API test project",
            "description": "Created by automated tests",
            "longitude": 77.0,
            "latitude": 20.0,
            "allocated_amount": 1000,
            "benchmark_amount": 1000,
            "data_source": "SYNTHETIC",
        },
    )
    assert created.status_code == 201, created.text
    project = created.json()
    assert project["code"] == code
    assert project["data_source"] == "SYNTHETIC"
    assert project["location"]["longitude"] == pytest.approx(77.0)
    fetched = client.get(f"/api/v1/projects/{project['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == project["id"]


def test_assess_unknown_project(client: TestClient):
    response = client.post(f"/api/v1/risks/assess/{uuid4()}")
    assert response.status_code == 404


def test_demo_project_assessment_if_seeded(client: TestClient):
    listing = client.get("/api/v1/projects", params={"q": "DEMO-001"})
    assert listing.status_code == 200
    items = listing.json()["items"]
    if not items:
        pytest.skip("demo seed not present")
    project_id = items[0]["id"]
    assessed = client.post(f"/api/v1/risks/assess/{project_id}")
    assert assessed.status_code == 200
    body = assessed.json()
    assert body["analysis_type"] == "RULE_BASED"
    assert body["data_source"] == "SYNTHETIC"
    assert body["source_module"]
    assert body["reason_text"]
    assert "does not establish fraud" in body["reason_text"].lower()
    codes = {item["signal_code"] for item in body["contributing_signals"]}
    assert {
        "duplicate_proximity",
        "image_similarity",
        "cost_deviation",
        "low_bidder_competition",
        "repeated_contractor_wins",
    }.issubset(codes)
    assert body["risk_score"] == 90
    assert body["risk_level"] == "CRITICAL"
    assert body["verification_status"] == "UNDER_REVIEW"
    evidence = client.get(f"/api/v1/projects/{project_id}/evidence")
    assert evidence.status_code == 200
    assert len(evidence.json()) >= 1
