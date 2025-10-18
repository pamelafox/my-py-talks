"""
=============================== tests coverage ================================
______________ coverage: platform linux, python 3.12.11-final-0 _______________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190     37    81%   34-35, 100, 102, 130, 150, 155, 158-161, 174-179, 278, 281, 284, 320, 322, 371-372, 374, 376, 378, 386, 398, 406-409, 502-503, 508-509
---------------------------------------------------------------------
TOTAL                                     257     37    86%
============================== 7 passed in 4.31s ==============================
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from fastapi_app.postgres_models import Trip


def test_get_bees_active_defaults(test_client: TestClient):
    with freeze_time("2025-10-17"):
        # Changed to SF where there is data
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["lat"] == 37.7749
    assert data["meta"]["lon"] == -122.4194
    assert data["meta"]["start_date"] == "2025-09-17"
    assert data["meta"]["end_date"] == "2025-10-17"
    assert len(data["data"]) > 0


def test_get_bees_active_custom_dates(test_client: TestClient):
    response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&start_date=2025-06-01&end_date=2025-06-15")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["start_date"] == "2025-06-01"
    assert data["meta"]["end_date"] == "2025-06-15"
    assert data["meta"]["months"] == [6]


def test_get_bees_search(test_client: TestClient):
    response = test_client.get("/bees/search?q=bombus")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "bombus"
    assert len(data["data"]) > 0
    assert "bombus" in data["data"][0]["scientific_name"].lower()


def test_get_phenology_chart(test_client: TestClient):
    # First get a valid taxon_id
    response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) > 0
    taxon_id = data["data"][0]["taxon_id"]

    response = test_client.get(f"/bees/phenology-chart/{taxon_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


@pytest.mark.asyncio
async def test_create_and_get_trip(test_client: TestClient, db_session):
    event_name = f"PyBay 2025 BioBlitz {uuid.uuid4().hex}"
    trip_data = {
        "event_name": event_name,
        "start_time": "2025-10-17T09:00:00",
        "end_time": "2025-10-17T17:00:00",
        "approx_latitude": 37.7749,
        "approx_longitude": -122.4194,
        "organizers": [{"display_name": "Pamela Fox"}],
    }
    response = test_client.post("/trips", json=trip_data)
    assert response.status_code == 201
    data = response.json()
    trip_id = data["id"]
    assert data["event_name"] == event_name
    assert data["organizers"][0]["original"] == "Pamela Fox"

    # Verify it was saved to the database
    trip = await db_session.get(Trip, trip_id)
    assert trip is not None
    assert trip.event_name == event_name

    # Test GET for the created trip
    response = test_client.get(f"/trips/{trip_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trip_id
    assert data["event_name"] == event_name


def test_list_trips(test_client: TestClient):
    # First create a trip to ensure there's at least one
    event_name = f"Test Trip for Listing {uuid.uuid4().hex}"
    trip_data = {
        "event_name": event_name,
        "start_time": "2025-08-01T10:00:00",
        "end_time": "2025-08-01T11:00:00",
        "approx_latitude": 34.0522,
        "approx_longitude": -118.2437,
        "organizers": [{"display_name": "Test Organizer"}],
    }
    test_client.post("/trips", json=trip_data)

    response = test_client.get("/trips?since=2025-08-01&before=2025-08-02")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["count"] >= 1
    assert any(t["event_name"] == event_name for t in data["data"])


def test_get_trip_not_found(test_client: TestClient):
    response = test_client.get("/trips/999999")
    assert response.status_code == 404
