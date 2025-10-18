from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from fastapi_app.api.models import TripCreate
from fastapi_app.api.routes import (
    bees_active,
    bees_phenology_chart,
    bees_search,
    create_trip,
    get_trip,
    list_trips,
)
from fastapi_app.postgres_models import Observation, Species

# ---------------------- Bee Activity: /bees/active ----------------------


def test_bees_active_no_candidates(test_client):
    # Choose a location likely far from any observations to trigger empty candidates early return
    resp = test_client.get(
        "/bees/active",
        params={
            "lat": 0.0,
            "lon": 0.0,
            "radius_km": 1,
            # no dates provided -> defaults applied
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["count"] == 0
    assert data["meta"]["candidate_count"] == 0
    # defaults applied when any date omitted
    assert "defaulted_dates" not in data["meta"]


@pytest.mark.asyncio
async def test_bees_active_with_data_and_branches(test_client, db_session):
    # Find one observation with coordinates and a valid month
    row = (
        (await db_session.execute(select(Observation).where(Observation.geom.is_not(None)).limit(1))).scalars().first()
    )
    assert row is not None, "Test DB must have at least one observation with coordinates"

    # Build a small window within observed_month
    # Use any year/day as only month matters; window <= 31 days
    start = datetime(2025, int(row.observed_month), 1).date()
    end = start + timedelta(days=7)

    # absolute_activity=True path; sort variants executed even if few items
    for sort in ["activity_desc", "activity_asc", "peak_month", "taxon_id"]:
        resp = test_client.get(
            "/bees/active",
            params={
                "lat": float(row.latitude or 0.0),
                "lon": float(row.longitude or 0.0),
                "radius_km": 5,
                "start_date": str(start),
                "end_date": str(end),
                "min_activity": 0,  # be permissive
                "absolute_activity": True,
                "require_research_grade": False,
                "sort": sort,
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "data" in payload and "meta" in payload
        assert set(payload["meta"]["months"]) == {start.month, end.month}

    # Normalized activity branch
    resp2 = test_client.get(
        "/bees/active",
        params={
            "lat": float(row.latitude or 0.0),
            "lon": float(row.longitude or 0.0),
            "radius_km": 5,
            "start_date": str(start),
            "end_date": str(end),
            "min_activity": 0,
            "absolute_activity": False,
            "require_research_grade": True,
        },
    )
    assert resp2.status_code == 200


def test_bees_active_invalid_dates(test_client):
    # end before start
    r1 = test_client.get(
        "/bees/active",
        params={
            "lat": 10,
            "lon": 10,
            "start_date": "2025-05-10",
            "end_date": "2025-05-01",
        },
    )
    assert r1.status_code == 422

    # invalid parse
    r2 = test_client.get(
        "/bees/active",
        params={
            "lat": 10,
            "lon": 10,
            "start_date": "2025-13-01",
        },
    )
    assert r2.status_code == 422

    # window > 31 days
    r3 = test_client.get(
        "/bees/active",
        params={
            "lat": 10,
            "lon": 10,
            "start_date": "2025-01-01",
            "end_date": "2025-03-15",
        },
    )
    assert r3.status_code == 422


# ---------------------- Species Search: /bees/search ----------------------


@pytest.mark.asyncio
async def test_bees_search_success_and_validation(test_client, db_session):
    # Grab a species scientific name prefix to ensure a match
    sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None, "Test DB must have at least one species"
    query = sp.scientific_name[:3]

    ok = test_client.get("/bees/search", params={"q": query, "limit": 10})
    assert ok.status_code == 200
    data = ok.json()
    assert data["query"] == query
    assert data["count"] <= 10

    # Too-short query should fail fastapi validation (422)
    bad = test_client.get("/bees/search", params={"q": "a"})
    assert bad.status_code == 422


# ----------------- Phenology Chart: /bees/phenology-chart/{taxon_id} -----------------


@pytest.mark.asyncio
async def test_bees_phenology_chart_png_and_404(test_client, db_session):
    # Find a species with window data to exercise highlight branch if possible
    sp = (
        (
            await db_session.execute(
                select(Species)
                .where(Species.window_start_all.is_not(None), Species.window_end_all.is_not(None))
                .limit(1)
            )
        )
        .scalars()
        .first()
    )
    if sp is None:
        # fallback to any species
        sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None

    r1 = test_client.get(f"/bees/phenology-chart/{sp.taxon_id}", params={"highlight_window": True})
    assert r1.status_code == 200
    assert r1.headers.get("content-type") == "image/png"
    # Summary header should exist
    assert r1.headers.get("X-Phenology-Summary") is not None

    # Toggle flags to exercise alternative code paths
    r2 = test_client.get(
        f"/bees/phenology-chart/{sp.taxon_id}",
        params={"require_research_grade": True, "highlight_window": False, "width": 640, "height": 360},
    )
    assert r2.status_code == 200

    # Not found
    not_found = test_client.get("/bees/phenology-chart/999999999")
    assert not_found.status_code == 404


# ---------------------- Trips ----------------------


def build_trip_payload(name_suffix: str = "") -> dict:
    now = datetime(2025, 5, 1, 9, 0, 0)
    later = now + timedelta(hours=2)
    uid = uuid.uuid4().hex[:8]
    return {
        "event_name": f"Fiësta Bee Bash{name_suffix} {uid}",
        "organizers": [
            {"display_name": "José Apiñón", "role": "Lead"},
            {"display_name": "  ", "role": "Ignore"},  # should be ignored
        ],
        "address_text": "Line1\n\nLine2\n",
        "country_hint": "US",
        "start_time": now.isoformat(),
        "end_time": later.isoformat(),
        "approx_latitude": 37.77,
        "approx_longitude": -122.42,
        "positional_accuracy_m": 50,
        "contact_emails": ["host@example.org"],
        "notes": "<script>alert('x')</script> Welcome!",
    }


def test_create_and_get_trip_roundtrip(test_client):
    payload = build_trip_payload(" 2025")
    resp = test_client.post("/trips", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["event_name"].startswith("Fiësta Bee Bash")
    # slugified, lowercase and hyphenated, no diacritics length-limited
    assert body["event_slug"].startswith("fi-sta-bee-bash-2025-")
    # organizers normalized (one ignored), diacritics flag
    assert len(body["organizers"]) == 1
    org = body["organizers"][0]
    assert org["original"] == "José Apiñón"
    assert isinstance(org["normalized"], str)
    assert isinstance(org["has_diacritics"], bool)
    # address only present when lines exist
    assert body["address"]["lines"] == ["Line1", "Line2"]
    # notes sanitized warning and content
    assert "notes: script/style tags removed" in body["warnings"]
    assert "<script" not in (body["notes_sanitized"] or "")

    # GET by id should work
    tid = body["id"]
    get_r = test_client.get(f"/trips/{tid}")
    assert get_r.status_code == 200
    got = get_r.json()
    assert got["id"] == tid
    assert got["time_window"]["duration_hours"] == 24.0  # fixed in get_trip

    # 404 branch
    not_found = test_client.get("/trips/99999999")
    assert not_found.status_code == 404


def test_create_trip_validation_errors(test_client):
    base = build_trip_payload()

    # end <= start
    bad1 = base | {"end_time": base["start_time"]}
    r1 = test_client.post("/trips", json=bad1)
    assert r1.status_code == 422

    # duration > 24h
    too_long = base | {"end_time": (datetime.fromisoformat(base["start_time"]) + timedelta(hours=25)).isoformat()}
    r2 = test_client.post("/trips", json=too_long)
    assert r2.status_code == 422

    # no organizers
    no_org = base | {"organizers": []}
    r3 = test_client.post("/trips", json=no_org)
    assert r3.status_code == 422

    # organizers all invalid (whitespace only)
    bad_org = base | {"organizers": [{"display_name": "  "}]}
    r4 = test_client.post("/trips", json=bad_org)
    assert r4.status_code == 422


def test_list_trips_filters(test_client):
    # Create two trips with different start dates
    p1 = build_trip_payload(" A")
    p2 = build_trip_payload(" B")
    # Adjust dates
    p1["start_time"] = "2025-05-01T09:00:00"
    p1["end_time"] = "2025-05-01T10:00:00"
    p2["start_time"] = "2025-06-15T09:00:00"
    p2["end_time"] = "2025-06-15T10:00:00"
    assert test_client.post("/trips", json=p1).status_code == 201
    assert test_client.post("/trips", json=p2).status_code == 201

    # since filter
    r_since = test_client.get("/trips", params={"since": "2025-06-01"})
    assert r_since.status_code == 200
    data_since = r_since.json()["data"]
    assert all(item["start_time"] >= "2025-06-01" for item in data_since)

    # before filter
    r_before = test_client.get("/trips", params={"before": "2025-06-01"})
    assert r_before.status_code == 200
    data_before = r_before.json()["data"]
    assert all(item["start_time"] < "2025-06-01" for item in data_before)

    # invalid dates
    assert test_client.get("/trips", params={"since": "invalid"}).status_code == 422
    assert test_client.get("/trips", params={"before": "invalid"}).status_code == 422


def test_create_trip_no_address_or_notes(test_client):
    now = datetime(2025, 8, 1, 9, 0, 0)
    later = now + timedelta(hours=2)
    payload = {
        "event_name": f"Minimal Trip {now.timestamp()} {uuid.uuid4().hex[:6]}",
        "organizers": [{"display_name": "Bob"}],
        "address_text": "\n\n",  # blanks -> no lines
        "country_hint": "US",
        "start_time": now.isoformat(),
        "end_time": later.isoformat(),
        "notes": None,
    }
    resp = test_client.post("/trips", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["address"] is None
    # No notes -> no warnings
    assert body["warnings"] == []


@pytest.mark.asyncio
async def test_bees_active_direct_no_candidates(db_session):
    res = await bees_active(
        db_session,
        lat=0.0,
        lon=0.0,
        start_date=None,
        end_date=None,
        radius_km=1,
        candidate_cap=800,
    )
    assert res.meta is not None
    assert res.meta.get("candidate_count") == 0


@pytest.mark.asyncio
async def test_bees_active_direct_with_candidates(db_session):
    # Get an observation with concrete lat/lon + geom
    row = (
        (
            await db_session.execute(
                select(Observation)
                .where(
                    Observation.geom.is_not(None), Observation.latitude.is_not(None), Observation.longitude.is_not(None)
                )
                .limit(1)
            )
        )
        .scalars()
        .first()
    )
    assert row is not None

    start = datetime(2025, int(row.observed_month), 1).date()
    end = start + timedelta(days=7)

    # Hit both absolute and normalized, multiple sort modes
    for absolute in (True, False):
        for sort in ("activity_desc", "activity_asc", "peak_month", "taxon_id"):
            out = await bees_active(
                db_session,
                lat=float(row.latitude),
                lon=float(row.longitude),
                start_date=str(start),
                end_date=str(end),
                radius_km=10,
                min_activity=0,
                sort=sort,
                require_research_grade=not absolute,
                absolute_activity=absolute,
                limit=25,
                candidate_cap=800,
            )
            assert out.meta is not None
            assert set(out.meta["months"]) == {start.month, end.month}


@pytest.mark.asyncio
async def test_bees_search_direct(db_session):
    sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None
    q = sp.scientific_name.split()[0]
    out = await bees_search(db_session, q=q, limit=5)
    assert out.query == q
    assert out.count <= 5


@pytest.mark.asyncio
async def test_bees_phenology_chart_direct(db_session):
    sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None
    resp = await bees_phenology_chart(sp.taxon_id, db_session, highlight_window=True, width=640, height=360)
    assert resp.headers.get("Content-Type", resp.headers.get("content-type")) == "image/png"


@pytest.mark.asyncio
async def test_bees_active_min_activity_filters(db_session):
    row = (
        (
            await db_session.execute(
                select(Observation)
                .where(
                    Observation.geom.is_not(None), Observation.latitude.is_not(None), Observation.longitude.is_not(None)
                )
                .limit(1)
            )
        )
        .scalars()
        .first()
    )
    assert row is not None
    start = datetime(2025, int(row.observed_month), 1).date()
    end = start + timedelta(days=7)
    # absolute_activity branch: force min_activity so high that all candidates continue
    out_abs = await bees_active(
        db_session,
        lat=float(row.latitude),
        lon=float(row.longitude),
        start_date=str(start),
        end_date=str(end),
        radius_km=10,
        min_activity=10_000_000,  # higher than any window sum
        sort="activity_desc",
        require_research_grade=False,
        absolute_activity=True,
        limit=25,
        candidate_cap=800,
    )
    assert out_abs.meta is not None
    # normalized branch: set threshold above 1
    out_norm = await bees_active(
        db_session,
        lat=float(row.latitude),
        lon=float(row.longitude),
        start_date=str(start),
        end_date=str(end),
        radius_km=10,
        min_activity=2.0,
        sort="activity_desc",
        require_research_grade=True,
        absolute_activity=False,
        limit=25,
        candidate_cap=800,
    )
    assert out_norm.meta is not None


@pytest.mark.asyncio
async def test_bees_phenology_chart_arrays_and_formatting(db_session):
    sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None
    # Set arrays to bad lengths to trigger normalization branches, and large counts to trigger formatting
    sp.phenology_normalized_all = [0.1] * 11  # bad length -> should reset to zeros
    sp.phenology_counts_all = [2_000_000] + [0] * 11  # trigger 'M' format
    sp.peak_month_all = 1  # trigger peak color branch
    sp.window_start_all = 2
    sp.window_end_all = 3
    await db_session.flush()
    r1 = await bees_phenology_chart(sp.taxon_id, db_session, highlight_window=True, width=640, height=360)
    assert r1.headers.get("content-type") == "image/png"
    # Now trigger 'K' format branch
    sp.phenology_counts_all = [5000] + [0] * 11
    await db_session.flush()
    r2 = await bees_phenology_chart(sp.taxon_id, db_session, highlight_window=True, width=640, height=360)
    assert r2.headers.get("content-type") == "image/png"
    # Research-grade branch, set invalid arrays as well
    sp.phenology_normalized = [0.2] * 10
    sp.phenology_counts = [2000] + [0] * 11
    await db_session.flush()
    r3 = await bees_phenology_chart(sp.taxon_id, db_session, require_research_grade=True, width=640, height=360)
    assert r3.headers.get("content-type") == "image/png"


@pytest.mark.asyncio
async def test_bees_phenology_chart_not_found(db_session):
    with pytest.raises(HTTPException) as ei:
        await bees_phenology_chart(0, db_session, width=640, height=360)
    assert ei.value.status_code == 404


@pytest.mark.asyncio
async def test_get_trip_not_found(db_session):
    with pytest.raises(HTTPException) as ei:
        await get_trip(db_session, 999999999)
    assert ei.value.status_code == 404


@pytest.mark.asyncio
async def test_create_trip_invalid_timestamps(db_session):
    bad = TripCreate(
        event_name="Bad Trip",
        organizers=[{"display_name": "X"}],
        address_text=None,
        country_hint="US",
        start_time="not-a-date",
        end_time="also-bad",
        approx_latitude=None,
        approx_longitude=None,
        positional_accuracy_m=None,
        contact_emails=None,
        notes=None,
    )
    with pytest.raises(HTTPException) as ei:
        await create_trip(db_session, bad)
    assert ei.value.status_code == 422


@pytest.mark.asyncio
async def test_bees_phenology_chart_counts_fallback_and_peak_color(db_session):
    sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None
    # Force counts fallback
    sp.phenology_counts_all = [1, 2, 3]
    sp.phenology_normalized_all = [0.0] * 12
    sp.peak_month_all = 1
    sp.window_start_all = 4
    sp.window_end_all = 5
    await db_session.flush()
    resp = await bees_phenology_chart(sp.taxon_id, db_session, highlight_window=True, width=640, height=360)
    assert resp.headers.get("content-type") == "image/png"


@pytest.mark.asyncio
async def test_bees_phenology_chart_cover_remaining_branches_all_obs(db_session):
    sp = (await db_session.execute(select(Species).limit(1))).scalars().first()
    assert sp is not None
    # 1) Trigger counts fallback (len != 12)
    sp.phenology_counts_all = [1, 2, 3]
    sp.phenology_normalized_all = [0.0] * 12
    sp.peak_month_all = None
    sp.window_start_all = None
    sp.window_end_all = None
    await db_session.flush()
    r_fallback = await bees_phenology_chart(
        sp.taxon_id,
        db_session,
        require_research_grade=False,
        width=640,
        height=360,
    )
    assert r_fallback.headers.get("content-type") == "image/png"

    # 2) Trigger peak color append, axvspan highlight, and 'M' formatting
    sp.phenology_counts_all = [2_000_000] + [0] * 11  # 'M' format
    sp.phenology_normalized_all = [0.1] * 12
    sp.peak_month_all = 1  # ensures peak color path
    sp.window_start_all = 2
    sp.window_end_all = 3
    await db_session.flush()
    r_all = await bees_phenology_chart(
        sp.taxon_id,
        db_session,
        require_research_grade=False,
        highlight_window=True,
        width=640,
        height=360,
    )
    assert r_all.headers.get("content-type") == "image/png"


def build_payload_unique() -> TripCreate:
    now = datetime(2025, 7, 1, 8, 0, 0)
    later = now + timedelta(hours=3)
    return TripCreate(
        event_name=f"Unit Trip {now.timestamp()} {uuid.uuid4().hex[:6]}",
        organizers=[{"display_name": "Alice", "role": "Lead"}],
        address_text="Addr1\nAddr2",
        country_hint="US",
        start_time=now.isoformat(),
        end_time=later.isoformat(),
        approx_latitude=37.0,
        approx_longitude=-122.0,
        positional_accuracy_m=30,
        contact_emails=["a@example.org"],
        notes="Hello",
    )


@pytest.mark.asyncio
async def test_trip_crud_direct(db_session):
    payload = build_payload_unique()
    created = await create_trip(db_session, payload)
    assert created.id > 0
    fetched = await get_trip(db_session, created.id)
    assert fetched.id == created.id
    # list filters
    lst = await list_trips(db_session, since=str(datetime(2025, 1, 1).date()), before=None)
    assert lst.meta["count"] >= 1
