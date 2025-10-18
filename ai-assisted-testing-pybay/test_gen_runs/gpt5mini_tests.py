"""
=============================== tests coverage ================================
______________ coverage: platform linux, python 3.12.11-final-0 _______________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190     37    81%   34-35, 100, 102, 130, 150, 155, 158-161, 174-179, 278, 281, 284, 320, 322, 371-372, 374, 376, 378, 386, 398, 462, 502-503, 505-509
---------------------------------------------------------------------
TOTAL                                     257     37    86%
============================== 4 passed in 2.73s ==============================
"""
import uuid


def test_bees_search(test_client):
    """Search should return species matching the query string."""
    resp = test_client.get("/bees/search", params={"q": "Apis", "limit": 10})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["query"] == "Apis"
    assert isinstance(body["data"], list)
    assert body["count"] == len(body["data"])
    # Expect at least one result that references Apis (honey bee) in either name or taxon id
    assert any(
        (item.get("taxon_id") == 47219) or ("Apis" in (item.get("scientific_name") or ""))
        for item in body["data"]
    )


def test_phenology_chart_returns_image_and_summary(test_client):
    """Phenology chart should return a PNG and include a summary header."""
    # Use a common taxon id that is present in the seeded observations (Apis mellifera)
    taxon_id = 47219
    resp = test_client.get(f"/bees/phenology-chart/{taxon_id}")
    assert resp.status_code == 200, resp.text
    # Binary image expected
    ctype = resp.headers.get("content-type", "")
    assert ctype.startswith("image/"), f"unexpected content-type: {ctype}"
    summary = resp.headers.get("X-Phenology-Summary") or resp.headers.get("x-phenology-summary")
    assert summary is not None
    assert "Apis" in summary or "apis" in summary.lower()


def test_bees_active_endpoint_basic(test_client):
    """Bees active should return data/meta envelope for a spatial/temporal query."""
    params = {
        "lat": 37.77,
        "lon": -122.42,
        "start_date": "2012-06-01",
        "end_date": "2012-06-30",
        "radius_km": 50,
        "limit": 10,
        "min_activity": 0,
    }
    resp = test_client.get("/bees/active", params=params)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body and "meta" in body
    # meta should echo requested dates
    assert body["meta"].get("start_date") == params["start_date"]
    assert body["meta"].get("end_date") == params["end_date"]
    # candidate_count should be present and >= reported count
    cand = body["meta"].get("candidate_count")
    cnt = body["meta"].get("count")
    assert isinstance(cand, int)
    assert isinstance(cnt, int)
    assert cand >= cnt


def test_trips_create_get_and_list(test_client):
    """Create a trip, fetch it by id, and verify it appears in the list endpoint."""
    # Make a reasonably unique event name to avoid collisions
    suffix = uuid.uuid4().hex[:8]
    event_name = f"PyTest Trip {suffix}"
    notes = "Focus: early survey <script>alert('x')</script>"
    payload = {
        "event_name": event_name,
        "organizers": [{"display_name": "Test Organizer", "role": "lead"}],
        "address_text": "1 Test Rd\nUnit 2",
        "country_hint": "US",
        # NOTE: use ISO strings accepted by datetime.fromisoformat (no trailing Z)
        "start_time": "2025-04-12T08:30:00+00:00",
        "end_time": "2025-04-12T12:00:00+00:00",
        "approx_latitude": 37.09,
        "approx_longitude": -121.91,
        "positional_accuracy_m": 1000,
        "contact_emails": ["team@example.test"],
        "notes": notes,
    }

    post = test_client.post("/trips", json=payload)
    assert post.status_code == 201, post.text
    created = post.json()
    assert created["event_name"] == event_name
    # notes should be sanitized (script tags removed)
    assert created.get("notes_sanitized") is not None
    assert "script" not in (created.get("notes_sanitized") or "").lower()
    # warnings should mention script/style removal
    assert any("script" in w or "style" in w for w in (created.get("warnings") or []))

    trip_id = created.get("id")
    assert isinstance(trip_id, int)

    # Fetch by id
    getr = test_client.get(f"/trips/{trip_id}")
    assert getr.status_code == 200, getr.text
    got = getr.json()
    assert got["id"] == trip_id
    assert got["event_name"] == event_name

    # Ensure it shows up in the list endpoint when filtering by since date
    list_resp = test_client.get("/trips", params={"since": "2025-04-01"})
    assert list_resp.status_code == 200, list_resp.text
    list_body = list_resp.json()
    assert "data" in list_body and "meta" in list_body
    assert any(item["event_name"] == event_name for item in list_body["data"]) 
