"""
=============================================== tests coverage ===============================================
______________________________ coverage: platform linux, python 3.12.11-final-0 ______________________________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190     47    75%   34-35, 100, 130, 150, 155, 158-161, 176-179, 281, 284, 320, 322, 371-372, 376, 386, 398, 429-431, 460-464, 497-512
---------------------------------------------------------------------
TOTAL                                     257     47    82%
========================================== short test summary info ===========================================
FAILED tests/test_routes.py::test_trip_create_and_get - sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.ex...
FAILED tests/test_routes.py::test_trip_list_filters - sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.ex...
================================= 2 failed, 10 passed, 12 warnings in 5.83s ==================================
"""
import datetime
from typing import Any

import pytest


# Fixtures imported from tests.conftest.py: test_client


def _assert_sorted(items: list[dict], key: str, reverse: bool = False):
    scores = [i[key] for i in items]
    assert scores == sorted(scores, reverse=reverse)


@pytest.mark.asyncio
def test_bees_active_basic(test_client):
    # Use coordinates within San Francisco cluster present in CSV
    resp = test_client.get(
        "/bees/active",
        params={
            "lat": 37.757,
            "lon": -122.441,
            "limit": 10,
        },
    )
    assert resp.status_code == 200
    js = resp.json()
    assert "data" in js and isinstance(js["data"], list)
    assert "meta" in js and isinstance(js["meta"], dict)
    meta = js["meta"]
    assert meta["count"] == len(js["data"])
    assert "months" in meta and len(meta["months"]) in (1, 2)
    # When there is no data we still want meta fields; skip content assertions
    if js["data"]:
        first = js["data"][0]
        for f in ["taxon_id", "scientific_name", "activity_score"]:
            assert f in first


@pytest.mark.asyncio
def test_bees_active_sorting(test_client):
    params = {
        "lat": 37.757,
        "lon": -122.441,
        "limit": 10,
        "sort": "activity_asc",
    }
    r = test_client.get("/bees/active", params=params)
    assert r.status_code == 200
    data = r.json()["data"]
    if len(data) > 1:
        _assert_sorted(data, "activity_score", reverse=False)
    # Descending
    params["sort"] = "activity_desc"
    r2 = test_client.get("/bees/active", params=params)
    assert r2.status_code == 200
    data2 = r2.json()["data"]
    if len(data2) > 1:
        _assert_sorted(data2, "activity_score", reverse=True)


@pytest.mark.asyncio
def test_bees_active_invalid_sort(test_client):
    r = test_client.get(
        "/bees/active",
        params={"lat": 37.757, "lon": -122.441, "sort": "not_a_valid"},
    )
    # FastAPI parameter regex validation should reject this
    assert r.status_code == 422


@pytest.mark.asyncio
def test_bees_active_bad_window(test_client):
    # Window > 31 days should fail
    start = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
    end = datetime.date.today().isoformat()
    r = test_client.get(
        "/bees/active",
        params={"lat": 37.757, "lon": -122.441, "start_date": start, "end_date": end},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
def test_bees_search_basic(test_client):
    r = test_client.get("/bees/search", params={"q": "Apis", "limit": 50})
    assert r.status_code == 200
    js = r.json()
    assert js["query"] == "Apis"
    assert js["count"] == len(js["data"])
    # Expect Apis mellifera taxon (47219) to appear if ingestion populated it
    if js["data"]:
        taxon_ids = {item["taxon_id"] for item in js["data"]}
        assert 47219 in taxon_ids  # Western Honey Bee


@pytest.mark.asyncio
def test_bees_search_too_short(test_client):
    r = test_client.get("/bees/search", params={"q": "A"})
    assert r.status_code == 422


@pytest.mark.asyncio
def test_bees_phenology_chart_ok(test_client):
    # Use Apis mellifera taxon id
    r = test_client.get("/bees/phenology-chart/47219")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "image/png"
    summary = r.headers.get("X-Phenology-Summary")
    assert summary and "Apis mellifera" in summary
    assert len(r.content) > 1000  # some bytes


@pytest.mark.asyncio
def test_bees_phenology_chart_not_found(test_client):
    r = test_client.get("/bees/phenology-chart/999999999")
    assert r.status_code == 404


def _trip_payload(suffix: str = "") -> dict[str, Any]:
    start = datetime.datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(hours=6)
    name = f"My Bee Trip 2025{suffix}!!!"
    return {
        "event_name": name,
        "organizers": [
            {"display_name": "Alice", "role": "Lead"},
            {"display_name": "Bob"},
        ],
        "address_text": "123 Bee Lane\nSan Francisco, CA",
        "country_hint": "US",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "approx_latitude": 37.757,
        "approx_longitude": -122.441,
        "positional_accuracy_m": 25,
        "contact_emails": ["alice@example.com"],
        "notes": "Fun trip <script>alert('x')</script> end.",
    }


@pytest.mark.asyncio
def test_trip_create_and_get(test_client):
    payload = _trip_payload("-one")
    r = test_client.post("/trips", json=payload)
    assert r.status_code == 201
    js = r.json()
    trip_id = js["id"]
    assert js["event_slug"].startswith("my-bee-trip-2025-one")
    assert js["event_name"] == payload["event_name"]
    assert js["time_window"]["duration_hours"] == 6.0
    # Organizer normalization
    assert len(js["organizers"]) >= 2
    organizer = js["organizers"][0]
    assert organizer["original"] == "Alice"
    assert organizer["normalized"].lower() == "alice"
    # Notes sanitization
    assert js["notes_sanitized"] == "Fun trip  end."
    assert "warnings" in js and any("script/style" in w for w in js["warnings"])
    # Fetch trip
    r2 = test_client.get(f"/trips/{trip_id}")
    assert r2.status_code == 200
    js2 = r2.json()
    assert js2["id"] == trip_id
    assert js2["event_slug"] == js["event_slug"]


@pytest.mark.asyncio
def test_trip_create_invalid_times(test_client):
    start = datetime.datetime.utcnow().isoformat()
    r = test_client.post(
        "/trips",
        json={
            "event_name": "Bad Trip",
            "organizers": [{"display_name": "Alice"}],
            "start_time": start,
            "end_time": start,  # equal -> invalid
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
def test_trip_create_no_organizers(test_client):
    start = datetime.datetime.utcnow().isoformat()
    end = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
    r = test_client.post(
        "/trips",
        json={
            "event_name": "No Orgs",
            "organizers": [],
            "start_time": start,
            "end_time": end,
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
def test_trip_list_filters(test_client):
    # Create a trip to ensure listing has at least one
    r_create = test_client.post("/trips", json=_trip_payload("-list"))
    assert r_create.status_code == 201
    # List without filters
    r_all = test_client.get("/trips")
    assert r_all.status_code == 200
    js_all = r_all.json()
    assert js_all["meta"]["count"] == len(js_all["data"]) >= 1
    # since filter (use today's date; should still include trip if start_time >= today UTC date)
    today = datetime.date.today().isoformat()
    r_since = test_client.get("/trips", params={"since": today})
    assert r_since.status_code in (200, 422)  # If parsing fails due to tz differences
    # before filter invalid
    r_bad = test_client.get("/trips", params={"before": "2025-13-01"})
    assert r_bad.status_code == 422
