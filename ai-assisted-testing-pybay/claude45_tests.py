"""
====================================== tests coverage =======================================
_____________________ coverage: platform linux, python 3.12.11-final-0 ______________________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190      7    96%   130, 281, 284, 320, 322, 386, 398
---------------------------------------------------------------------
TOTAL                                     257      7    97%
==================================== 61 passed in 11.24s ====================================
"""
import uuid


class TestBeesActive:
    """Test the /bees/active endpoint."""

    def test_bees_active_basic(self, test_client):
        """Test basic active bees query with required parameters."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)
        assert "count" in data["meta"]
        assert "lat" in data["meta"]
        assert "lon" in data["meta"]

    def test_bees_active_with_date_range(self, test_client):
        """Test active bees with specific date range."""
        response = test_client.get(
            "/bees/active?lat=37.7749&lon=-122.4194&start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["start_date"] == "2024-01-01"
        assert data["meta"]["end_date"] == "2024-01-31"
        assert data["meta"]["defaulted_dates"] is False

    def test_bees_active_default_dates(self, test_client):
        """Test active bees with default dates."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["defaulted_dates"] is True
        assert "start_date" in data["meta"]
        assert "end_date" in data["meta"]

    def test_bees_active_with_radius(self, test_client):
        """Test active bees with custom radius."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&radius_km=50")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["radius_km"] == 50

    def test_bees_active_with_limit(self, test_client):
        """Test active bees with custom limit."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_bees_active_sort_activity_desc(self, test_client):
        """Test active bees sorted by activity descending."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=activity_desc")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            scores = [item["activity_score"] for item in data["data"]]
            assert scores == sorted(scores, reverse=True)

    def test_bees_active_sort_activity_asc(self, test_client):
        """Test active bees sorted by activity ascending."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=activity_asc")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            scores = [item["activity_score"] for item in data["data"]]
            assert scores == sorted(scores)

    def test_bees_active_sort_peak_month(self, test_client):
        """Test active bees sorted by peak month."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=peak_month")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["sort"] == "peak_month"

    def test_bees_active_sort_taxon_id(self, test_client):
        """Test active bees sorted by taxon_id."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=taxon_id")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            taxon_ids = [item["taxon_id"] for item in data["data"]]
            assert taxon_ids == sorted(taxon_ids)

    def test_bees_active_research_grade(self, test_client):
        """Test active bees with research grade filter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&require_research_grade=true")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["require_research_grade"] is True

    def test_bees_active_absolute_activity(self, test_client):
        """Test active bees with absolute activity mode."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&absolute_activity=true")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["absolute_activity"] is True

    def test_bees_active_relative_activity(self, test_client):
        """Test active bees with relative activity mode."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&absolute_activity=false")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["absolute_activity"] is False

    def test_bees_active_min_activity(self, test_client):
        """Test active bees with minimum activity threshold."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&min_activity=0.1")
        assert response.status_code == 200
        data = response.json()
        for item in data["data"]:
            assert isinstance(item["activity_score"], float)

    def test_bees_active_candidate_cap(self, test_client):
        """Test active bees with candidate cap."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&candidate_cap=100")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["candidate_cap"] == 100
        assert data["meta"]["candidate_count"] <= 100

    def test_bees_active_invalid_lat(self, test_client):
        """Test active bees with invalid latitude."""
        response = test_client.get("/bees/active?lat=100&lon=-122.4194")
        assert response.status_code == 422

    def test_bees_active_invalid_lon(self, test_client):
        """Test active bees with invalid longitude."""
        response = test_client.get("/bees/active?lat=37.7749&lon=200")
        assert response.status_code == 422

    def test_bees_active_missing_required_params(self, test_client):
        """Test active bees without required parameters."""
        response = test_client.get("/bees/active")
        assert response.status_code == 422

    def test_bees_active_invalid_date_format(self, test_client):
        """Test active bees with invalid date format."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&start_date=invalid")
        assert response.status_code == 422

    def test_bees_active_end_before_start(self, test_client):
        """Test active bees with end date before start date."""
        response = test_client.get(
            "/bees/active?lat=37.7749&lon=-122.4194&start_date=2024-12-31&end_date=2024-01-01"
        )
        assert response.status_code == 422

    def test_bees_active_window_too_large(self, test_client):
        """Test active bees with date window exceeding 31 days."""
        response = test_client.get(
            "/bees/active?lat=37.7749&lon=-122.4194&start_date=2024-01-01&end_date=2024-02-15"
        )
        assert response.status_code == 422

    def test_bees_active_invalid_sort(self, test_client):
        """Test active bees with invalid sort parameter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=invalid")
        assert response.status_code == 422

    def test_bees_active_response_structure(self, test_client):
        """Test that active bees response has correct structure."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&limit=1")
        assert response.status_code == 200
        data = response.json()
        if data["data"]:
            item = data["data"][0]
            assert "taxon_id" in item
            assert "scientific_name" in item
            assert "common_name" in item
            assert "activity_score" in item
            assert "peak_month" in item


class TestBeesSearch:
    """Test the /bees/search endpoint."""

    def test_bees_search_basic(self, test_client):
        """Test basic species search."""
        response = test_client.get("/bees/search?q=bee")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "count" in data
        assert "data" in data
        assert data["query"] == "bee"
        assert isinstance(data["data"], list)

    def test_bees_search_with_limit(self, test_client):
        """Test species search with custom limit."""
        response = test_client.get("/bees/search?q=bee&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_bees_search_common_name(self, test_client):
        """Test searching by common name."""
        response = test_client.get("/bees/search?q=bumble")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "bumble"

    def test_bees_search_scientific_name(self, test_client):
        """Test searching by scientific name."""
        response = test_client.get("/bees/search?q=apis")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "apis"

    def test_bees_search_multiple_words(self, test_client):
        """Test searching with multiple words."""
        response = test_client.get("/bees/search?q=honey%20bee")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "honey bee"

    def test_bees_search_no_results(self, test_client):
        """Test search with query that returns no results."""
        response = test_client.get("/bees/search?q=zzzznonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert len(data["data"]) == 0

    def test_bees_search_missing_query(self, test_client):
        """Test search without query parameter."""
        response = test_client.get("/bees/search")
        assert response.status_code == 422

    def test_bees_search_query_too_short(self, test_client):
        """Test search with query shorter than minimum length."""
        response = test_client.get("/bees/search?q=a")
        assert response.status_code == 422

    def test_bees_search_response_structure(self, test_client):
        """Test that search response has correct structure."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        data = response.json()
        if data["data"]:
            item = data["data"][0]
            assert "taxon_id" in item
            assert "scientific_name" in item
            assert "rank" in item
            assert "total_observations" in item
            assert "total_observations_all" in item
            assert "peak_month" in item
            assert "peak_month_all" in item
            assert "score" in item

    def test_bees_search_results_ordered_by_score(self, test_client):
        """Test that search results are ordered by relevance score."""
        response = test_client.get("/bees/search?q=bee")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            scores = [item["score"] for item in data["data"] if item["score"] is not None]
            assert scores == sorted(scores, reverse=True)


class TestBeesPhenologyChart:
    """Test the /bees/phenology-chart endpoint."""

    def test_phenology_chart_basic(self, test_client):
        """Test getting a phenology chart with default parameters."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            assert "X-Phenology-Summary" in response.headers

    def test_phenology_chart_with_dimensions(self, test_client):
        """Test phenology chart with custom dimensions."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?width=800&height=600")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

    def test_phenology_chart_with_highlight_window(self, test_client):
        """Test phenology chart with highlight window enabled."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?highlight_window=true")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

    def test_phenology_chart_research_grade(self, test_client):
        """Test phenology chart with research grade filter."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?require_research_grade=true")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

    def test_phenology_chart_not_found(self, test_client):
        """Test phenology chart for non-existent taxon."""
        response = test_client.get("/bees/phenology-chart/999999999")
        assert response.status_code == 404


class TestTripsCreate:
    """Test the POST /trips endpoint."""

    def test_create_trip_basic(self, test_client):
        """Test creating a basic trip."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Test Bee Walk {unique_id}",
            "organizers": [{"display_name": "John Doe", "role": "Lead"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T14:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert f"Test Bee Walk {unique_id}" in data["event_name"]
        assert len(data["organizers"]) == 1
        assert data["organizers"][0]["original"] == "John Doe"
        assert data["organizers"][0]["role"] == "Lead"
        assert data["time_window"]["duration_hours"] == 4.0

    def test_create_trip_with_location(self, test_client):
        """Test creating a trip with location data."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Coastal Bee Survey {unique_id}",
            "organizers": [{"display_name": "Jane Smith"}],
            "start_time": "2025-07-01T09:00:00",
            "end_time": "2025-07-01T12:00:00",
            "approx_latitude": 37.7749,
            "approx_longitude": -122.4194,
            "positional_accuracy_m": 100,
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["location"]["approx_latitude"] == 37.7749
        assert data["location"]["approx_longitude"] == -122.4194
        assert data["location"]["positional_accuracy_m"] == 100

    def test_create_trip_with_address(self, test_client):
        """Test creating a trip with address."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Park Bee Count {unique_id}",
            "organizers": [{"display_name": "Alice"}],
            "start_time": "2025-08-01T10:00:00",
            "end_time": "2025-08-01T15:00:00",
            "address_text": "123 Main St\nSan Francisco, CA 94102",
            "country_hint": "US",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["address"] is not None
        assert len(data["address"]["lines"]) == 2
        assert data["address"]["country"] == "US"

    def test_create_trip_with_contact_emails(self, test_client):
        """Test creating a trip with contact emails."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"University Bee Research {unique_id}",
            "organizers": [{"display_name": "Dr. Brown"}],
            "start_time": "2025-09-01T08:00:00",
            "end_time": "2025-09-01T16:00:00",
            "contact_emails": ["brown@university.edu"],
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201

    def test_create_trip_with_notes(self, test_client):
        """Test creating a trip with notes."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Garden Bee Watch {unique_id}",
            "organizers": [{"display_name": "Bob"}],
            "start_time": "2025-10-01T11:00:00",
            "end_time": "2025-10-01T13:00:00",
            "notes": "Bring sunscreen and water.",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["notes_sanitized"] == "Bring sunscreen and water."

    def test_create_trip_sanitizes_script_tags(self, test_client):
        """Test that script tags are removed from notes."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Test Event {unique_id}",
            "organizers": [{"display_name": "Charlie"}],
            "start_time": "2025-11-01T10:00:00",
            "end_time": "2025-11-01T12:00:00",
            "notes": "Safe text <script>alert('xss')</script> more text",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "<script>" not in data["notes_sanitized"]
        assert "Safe text" in data["notes_sanitized"]
        assert "notes: script/style tags removed" in data["warnings"]

    def test_create_trip_multiple_organizers(self, test_client):
        """Test creating a trip with multiple organizers."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Multi-Leader Bee Walk {unique_id}",
            "organizers": [
                {"display_name": "Leader One", "role": "Primary"},
                {"display_name": "Leader Two", "role": "Assistant"},
            ],
            "start_time": "2025-12-01T09:00:00",
            "end_time": "2025-12-01T11:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["organizers"]) == 2

    def test_create_trip_organizer_with_diacritics(self, test_client):
        """Test creating a trip with organizer name containing diacritics."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"International Bee Study {unique_id}",
            "organizers": [{"display_name": "José García"}],
            "start_time": "2025-06-20T10:00:00",
            "end_time": "2025-06-20T12:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["organizers"][0]["original"] == "José García"

    def test_create_trip_no_organizers(self, test_client):
        """Test that creating a trip without organizers fails."""
        payload = {
            "event_name": "No Leader Walk",
            "organizers": [],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T12:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422

    def test_create_trip_invalid_timestamps(self, test_client):
        """Test creating a trip with invalid timestamp format."""
        payload = {
            "event_name": "Bad Time Walk",
            "organizers": [{"display_name": "Test"}],
            "start_time": "not-a-timestamp",
            "end_time": "2025-06-15T12:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422

    def test_create_trip_end_before_start(self, test_client):
        """Test creating a trip with end time before start time."""
        payload = {
            "event_name": "Time Travel Walk",
            "organizers": [{"display_name": "Test"}],
            "start_time": "2025-06-15T12:00:00",
            "end_time": "2025-06-15T10:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422

    def test_create_trip_duration_too_long(self, test_client):
        """Test creating a trip with duration exceeding 24 hours."""
        payload = {
            "event_name": "Marathon Walk",
            "organizers": [{"display_name": "Test"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-16T11:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422

    def test_create_trip_slug_generation(self, test_client):
        """Test that trip slug is generated correctly."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Test Event With Spaces & Special!!! Characters {unique_id}",
            "organizers": [{"display_name": "Test"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T12:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "test-event-with-spaces-special-characters" in data["event_slug"]


class TestTripsGet:
    """Test the GET /trips/{trip_id} endpoint."""

    def test_get_trip(self, test_client):
        """Test getting a trip by ID."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Test Get Trip {unique_id}",
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T14:00:00",
        }
        create_response = test_client.post("/trips", json=payload)
        assert create_response.status_code == 201
        trip_id = create_response.json()["id"]

        get_response = test_client.get(f"/trips/{trip_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == trip_id
        assert f"Test Get Trip {unique_id}" in data["event_name"]

    def test_get_trip_not_found(self, test_client):
        """Test getting a non-existent trip."""
        response = test_client.get("/trips/999999999")
        assert response.status_code == 404

    def test_get_trip_response_structure(self, test_client):
        """Test that get trip response has correct structure."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"Structure Test {unique_id}",
            "organizers": [{"display_name": "Test"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T12:00:00",
            "approx_latitude": 37.7749,
            "approx_longitude": -122.4194,
        }
        create_response = test_client.post("/trips", json=payload)
        trip_id = create_response.json()["id"]

        response = test_client.get(f"/trips/{trip_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "event_slug" in data
        assert "event_name" in data
        assert "time_window" in data
        assert "location" in data
        assert "organizers" in data
        assert "warnings" in data
        assert "created_at" in data


class TestTripsList:
    """Test the GET /trips endpoint."""

    def test_list_trips_empty(self, test_client):
        """Test listing trips when none exist (or filtered out)."""
        response = test_client.get("/trips?since=2099-01-01")
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_list_trips_with_data(self, test_client):
        """Test listing trips after creating some."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"List Test Trip {unique_id}",
            "organizers": [{"display_name": "Test"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T12:00:00",
        }
        test_client.post("/trips", json=payload)

        response = test_client.get("/trips")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["count"] >= 1

    def test_list_trips_with_since_filter(self, test_client):
        """Test listing trips with since date filter."""
        response = test_client.get("/trips?since=2025-01-01")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["since"] == "2025-01-01"

    def test_list_trips_with_before_filter(self, test_client):
        """Test listing trips with before date filter."""
        response = test_client.get("/trips?before=2026-01-01")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["before"] == "2026-01-01"

    def test_list_trips_with_both_filters(self, test_client):
        """Test listing trips with both since and before filters."""
        response = test_client.get("/trips?since=2025-01-01&before=2026-01-01")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["since"] == "2025-01-01"
        assert data["meta"]["query"]["before"] == "2026-01-01"

    def test_list_trips_invalid_since_date(self, test_client):
        """Test listing trips with invalid since date."""
        response = test_client.get("/trips?since=invalid")
        assert response.status_code == 422

    def test_list_trips_invalid_before_date(self, test_client):
        """Test listing trips with invalid before date."""
        response = test_client.get("/trips?before=invalid")
        assert response.status_code == 422

    def test_list_trips_response_structure(self, test_client):
        """Test that list trips response has correct structure."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "event_name": f"List Structure Test {unique_id}",
            "organizers": [{"display_name": "Test"}],
            "start_time": "2025-06-15T10:00:00",
            "end_time": "2025-06-15T12:00:00",
        }
        test_client.post("/trips", json=payload)

        response = test_client.get("/trips")
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "query" in data["meta"]
        assert "count" in data["meta"]
        assert "data" in data
        if data["data"]:
            item = data["data"][0]
            assert "id" in item
            assert "event_name" in item
            assert "start_time" in item
