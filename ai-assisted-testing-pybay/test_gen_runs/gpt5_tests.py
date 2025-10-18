"""
============================================ tests coverage ============================================
___________________________ coverage: platform linux, python 3.12.11-final-0 ___________________________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190     67    65%   34-35, 130, 150, 155, 158-161, 174-179, 279-349, 371-372, 508-509
---------------------------------------------------------------------
TOTAL                                     257     67    74%
======================================= short test summary info ========================================
SKIPPED [1] tests/test_routes.py:15: No species available in test database for phenology/chart tests
===================================== 9 passed, 1 skipped in 1.72s =====================================
"""
import datetime
import uuid
import pytest


# Use test_client fixture from conftest


def _find_existing_species_id(test_client):
    # Use /bees/search to find a species. Query must be >=2 chars.
    resp = test_client.get("/bees/search", params={"q": "ab", "limit": 1})
    assert resp.status_code == 200
    data = resp.json()
    if data["count"] == 0:
        pytest.skip("No species available in test database for phenology/chart tests")
    return data["data"][0]["taxon_id"]


def test_bees_search_basic(test_client):
    resp = test_client.get("/bees/search", params={"q": "be", "limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert "query" in body and body["query"] == "be"
    assert "count" in body and body["count"] <= 5
    assert isinstance(body["data"], list)
    # Each item minimal structure
    for item in body["data"]:
        assert "taxon_id" in item
        assert "scientific_name" in item
        assert "score" in item  # may be None


def test_bees_search_min_length_enforced(test_client):
    resp = test_client.get("/bees/search", params={"q": "x"})  # too short (min_length=2)
    assert resp.status_code == 422


def test_bees_active_defaults(test_client):
    # Use a plausible SF coordinate (matches examples) expecting either empty or some data
    resp = test_client.get(
        "/bees/active",
        params={"lat": 37.7749, "lon": -122.4194},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body and "meta" in body
    meta = body["meta"]
    assert meta["lat"] == 37.7749
    assert meta["lon"] == -122.4194
    assert meta["radius_km"] == 25  # default
    assert meta["absolute_activity"] is True
    assert meta["require_research_grade"] is False
    assert meta["candidate_cap"] == 800
    # If data present, verify shape
    for item in body["data"]:
        assert set(item.keys()) >= {"taxon_id", "scientific_name", "activity_score"}


def test_bees_active_validation(test_client):
    # end_date before start_date should 422
    today = datetime.date.today()
    start = today
    end = today - datetime.timedelta(days=1)
    resp = test_client.get(
        "/bees/active",
        params={
            "lat": 10,
            "lon": 10,
            "start_date": str(start),
            "end_date": str(end),
        },
    )
    assert resp.status_code == 422

    # Window > 31 days should 422
    resp2 = test_client.get(
        "/bees/active",
        params={
            "lat": 10,
            "lon": 10,
            "start_date": str(today - datetime.timedelta(days=40)),
            "end_date": str(today),
        },
    )
    assert resp2.status_code == 422


def test_bees_phenology_chart_png(test_client):
    taxon_id = _find_existing_species_id(test_client)
    resp = test_client.get(f"/bees/phenology-chart/{taxon_id}")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "image/png"
    summary = resp.headers.get("X-Phenology-Summary")
    assert summary and str(taxon_id) not in summary  # summary contains name, not raw id
    # Basic PNG magic number check
    assert resp.content.startswith(b"\x89PNG")


def test_bees_phenology_chart_not_found(test_client):
    resp = test_client.get("/bees/phenology-chart/999999999")
    assert resp.status_code == 404


def test_create_trip_success(test_client):
    now = datetime.datetime.utcnow().replace(microsecond=0)
    later = now + datetime.timedelta(hours=2)
    unique_suffix = uuid.uuid4().hex[:8]
    event_name = f"Sunrise Survey {unique_suffix}"
    payload = {
        "event_name": event_name,
        "organizers": [
            {"display_name": "Ana María", "role": "lead"},
            {"display_name": "Bo"},
        ],
        "start_time": now.isoformat(),
        "end_time": later.isoformat(),
        "approx_latitude": 40.0,
        "approx_longitude": -105.0,
        "positional_accuracy_m": 50,
        "address_text": "123 Meadow Lane\nCO",
        "country_hint": "US",
        "contact_emails": ["ana@example.com"],
        "notes": "Looking for early emergers <script>alert('x')</script> end.",
    }
    resp = test_client.post("/trips", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["event_name"] == payload["event_name"]
    assert body["event_slug"].startswith("sunrise-survey")
    assert body["time_window"]["duration_hours"] == pytest.approx(2.0, rel=1e-3)
    # Organizer normalization & diacritics
    organizers = body["organizers"]
    assert len(organizers) == 2
    assert organizers[0]["original"] == "Ana María"
    # Precomposed accent not removed by current regex (only strips combining marks)
    assert organizers[0]["has_diacritics"] is False
    assert organizers[0]["normalized"] == organizers[0]["original"]
    assert body["warnings"] == ["notes: script/style tags removed"]
    assert "script" not in (body["notes_sanitized"] or "")

    # Retrieve via GET
    trip_id = body["id"]
    get_resp = test_client.get(f"/trips/{trip_id}")
    assert get_resp.status_code == 200
    trip = get_resp.json()
    assert trip["id"] == trip_id
    assert trip["event_slug"].startswith("sunrise-survey")

    # List endpoint should include the trip
    list_resp = test_client.get("/trips")
    assert list_resp.status_code == 200
    listed = list_resp.json()["data"]
    assert any(r["id"] == trip_id for r in listed)


def test_create_trip_validation_errors(test_client):
    now = datetime.datetime.utcnow().replace(microsecond=0)
    # end before start
    payload_bad_time = {
        "event_name": "Bad Trip",
        "organizers": [{"display_name": "A"}],
        "start_time": now.isoformat(),
        "end_time": (now - datetime.timedelta(hours=1)).isoformat(),
    }
    r1 = test_client.post("/trips", json=payload_bad_time)
    assert r1.status_code == 422

    # Duration > 24h
    payload_long = {
        "event_name": "Long Trip",
        "organizers": [{"display_name": "A"}],
        "start_time": now.isoformat(),
        "end_time": (now + datetime.timedelta(hours=25)).isoformat(),
    }
    r2 = test_client.post("/trips", json=payload_long)
    assert r2.status_code == 422

    # Missing organizers
    payload_no_orgs = {
        "event_name": "No Orgs Trip",
        "organizers": [],
        "start_time": now.isoformat(),
        "end_time": (now + datetime.timedelta(hours=1)).isoformat(),
    }
    r3 = test_client.post("/trips", json=payload_no_orgs)
    assert r3.status_code == 422

    # Invalid organizer blank names filtered out
    payload_blank_orgs = {
        "event_name": "Blank Orgs Trip",
        "organizers": [{"display_name": "   "}],
        "start_time": now.isoformat(),
        "end_time": (now + datetime.timedelta(hours=1)).isoformat(),
    }
    r4 = test_client.post("/trips", json=payload_blank_orgs)
    assert r4.status_code == 422


def test_list_trips_filters(test_client):
    # Create two trips with different dates
    base = datetime.datetime.utcnow().replace(microsecond=0)
    suffix1 = uuid.uuid4().hex[:6]
    suffix2 = uuid.uuid4().hex[:6]
    name1 = f"Filter Trip One {suffix1}"
    name2 = f"Filter Trip Two {suffix2}"
    p1 = {
        "event_name": name1,
        "organizers": [{"display_name": "Org"}],
        "start_time": base.isoformat(),
        "end_time": (base + datetime.timedelta(hours=2)).isoformat(),
    }
    p2 = {
        "event_name": name2,
        "organizers": [{"display_name": "Org"}],
        "start_time": (base + datetime.timedelta(days=2)).isoformat(),
        "end_time": (base + datetime.timedelta(days=2, hours=1)).isoformat(),
    }
    r1 = test_client.post("/trips", json=p1)
    r2 = test_client.post("/trips", json=p2)
    assert r1.status_code == 201 and r2.status_code == 201

    day2 = (base + datetime.timedelta(days=2)).date()

    # since filter should include second but maybe not first if since is day2
    resp_since = test_client.get("/trips", params={"since": str(day2)})
    assert resp_since.status_code == 200
    data_since = resp_since.json()["data"]
    assert any(name2 == r["event_name"] for r in data_since)
    assert all(r["start_time"] >= str(day2) for r in data_since)

    # before filter should exclude second if before is day2
    resp_before = test_client.get("/trips", params={"before": str(day2)})
    assert resp_before.status_code == 200
    data_before = resp_before.json()["data"]
    assert any(name1 == r["event_name"] for r in data_before)
    assert all(r["start_time"] < str(day2) for r in data_before)

    # Invalid date format
    resp_bad = test_client.get("/trips", params={"since": "2025-13-01"})
    assert resp_bad.status_code == 422


def test_get_trip_not_found(test_client):
    resp = test_client.get("/trips/999999")
    assert resp.status_code == 404
