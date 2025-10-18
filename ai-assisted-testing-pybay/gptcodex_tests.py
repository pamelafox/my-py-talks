"""
=============================== tests coverage ================================
______________ coverage: platform linux, python 3.12.11-final-0 _______________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190     29    85%   34-35, 102, 130, 150, 155, 158-161, 174-179, 281, 284, 320, 322, 371-372, 376, 378, 386, 398, 462, 508-509
---------------------------------------------------------------------
TOTAL                                     257     29    89%
============================== 9 passed in 2.48s ==============================
"""
"""Integration tests for FastAPI API routes."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.anyio


def test_bees_active_returns_results(test_client: TestClient) -> None:
    """It returns bee activity data in the requested search window."""
    params = {
        "lat": 37.7749,
        "lon": -122.4194,
        "start_date": "2012-03-01",
        "end_date": "2012-03-15",
        "radius_km": 50,
        "limit": 5,
    }
    response = test_client.get("/bees/active", params=params)
    assert response.status_code == 200
    body = response.json()
    assert body["data"], "Expected at least one active species"
    first_item = body["data"][0]
    assert isinstance(first_item["taxon_id"], int)
    assert body["meta"]["start_date"] == "2012-03-01"
    assert 3 in body["meta"]["months"]


def test_bees_active_rejects_invalid_range(test_client: TestClient) -> None:
    """It rejects requests where the end date precedes the start date."""
    params = {
        "lat": 37.7749,
        "lon": -122.4194,
        "start_date": "2012-03-10",
        "end_date": "2012-03-01",
    }
    response = test_client.get("/bees/active", params=params)
    assert response.status_code == 422
    assert response.json()["detail"] == "end_date must be >= start_date"


def test_bees_search_returns_ranked_species(test_client: TestClient) -> None:
    """It returns species that match the search query."""
    response = test_client.get("/bees/search", params={"q": "Apis", "limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "Apis"
    assert 0 < body["count"] <= 5
    assert any("Apis" in item["scientific_name"] for item in body["data"])


def test_bees_search_enforces_minimum_query_length(test_client: TestClient) -> None:
    """It enforces the minimum query length validation."""
    response = test_client.get("/bees/search", params={"q": "A"})
    assert response.status_code == 422


def test_bees_phenology_chart_returns_png(test_client: TestClient) -> None:
    """It returns a PNG image for a known taxon."""
    response = test_client.get("/bees/phenology-chart/47219")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-phenology-summary"].startswith("Apis mellifera")
    assert response.content


def test_bees_phenology_chart_missing_taxon(test_client: TestClient) -> None:
    """It returns a 404 error for unknown taxa."""
    response = test_client.get("/bees/phenology-chart/999999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Taxon not found"


def test_create_trip_persists_trip_state(test_client: TestClient) -> None:
    """It creates a trip and normalizes organizer data and notes."""
    unique_suffix = uuid.uuid4().hex[:8]
    start_time = datetime(2024, 5, 1, 9, 0, 0)
    end_time = start_time + timedelta(hours=6)
    payload = {
        "event_name": f"Test Trip Event {unique_suffix}",
        "organizers": [{"display_name": "Lead Organizer", "role": "Host"}],
        "address_text": "123 Bee Lane\nSan Francisco, CA",
        "country_hint": "US",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "approx_latitude": 37.77,
        "approx_longitude": -122.42,
        "positional_accuracy_m": 25,
        "contact_emails": ["host@example.com"],
        "notes": "<script>alert('x')</script>Plan for bees.",
    }
    response = test_client.post("/trips", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["event_slug"].startswith("test-trip-event-")
    assert body["time_window"]["duration_hours"] == 6.0
    assert body["notes_sanitized"] == "Plan for bees."
    assert body["warnings"] == ["notes: script/style tags removed"]
    assert body["address"] == {
        "lines": ["123 Bee Lane", "San Francisco, CA"],
        "country": "US",
    }
    assert body["organizers"][0]["role"] == "Host"

    trip_id = body["id"]
    detail_response = test_client.get(f"/trips/{trip_id}")
    assert detail_response.status_code == 200
    details = detail_response.json()
    assert details["event_name"] == payload["event_name"]
    assert details["time_window"]["start_time"] == "2024-05-01"
    assert details["notes_sanitized"] == "Plan for bees."

    list_response = test_client.get(
        "/trips",
        params={
            "since": "2024-04-01",
            "before": "2024-06-01",
        },
    )
    assert list_response.status_code == 200
    listing = list_response.json()
    assert listing["meta"]["query"] == {"since": "2024-04-01", "before": "2024-06-01"}
    assert any(item["id"] == trip_id for item in listing["data"])


def test_create_trip_rejects_invalid_time_window(test_client: TestClient) -> None:
    """It rejects trips where the end time is not after the start time."""
    payload = {
        "event_name": "Trip With Invalid Range",
        "organizers": [{"display_name": "Lead Organizer"}],
        "start_time": "2024-05-01T10:00:00",
        "end_time": "2024-05-01T09:00:00",
    }
    response = test_client.post("/trips", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"] == "end_time must be > start_time"


def test_list_trips_rejects_invalid_filters(test_client: TestClient) -> None:
    """It rejects list queries with invalid date filters."""
    response = test_client.get("/trips", params={"since": "not-a-date"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid since date"
