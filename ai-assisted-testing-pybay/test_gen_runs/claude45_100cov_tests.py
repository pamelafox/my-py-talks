"""
=========================================== tests coverage ============================================
__________________________ coverage: platform linux, python 3.12.11-final-0 ___________________________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190      4    98%   281, 284, 320, 322
---------------------------------------------------------------------
TOTAL                                     257      4    98%
========================================= 54 passed in 7.95s ==========================================
"""
class TestBeesActiveEndpoint:
    """Tests for /bees/active endpoint."""

    def test_bees_active_defaults(self, test_client):
        """Test with minimal required parameters using defaults."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)
        assert data["meta"]["lat"] == 37.7749
        assert data["meta"]["lon"] == -122.4194
        assert data["meta"]["defaulted_dates"] is True

    def test_bees_active_with_date_range(self, test_client):
        """Test with explicit date range."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&start_date=2024-04-01&end_date=2024-04-15")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["start_date"] == "2024-04-01"
        assert data["meta"]["end_date"] == "2024-04-15"
        assert data["meta"]["defaulted_dates"] is False

    def test_bees_active_with_radius(self, test_client):
        """Test with custom radius."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&radius_km=50")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["radius_km"] == 50

    def test_bees_active_with_limit(self, test_client):
        """Test limit parameter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_bees_active_activity_desc_sort(self, test_client):
        """Test sorting by activity descending."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=activity_desc")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            scores = [item["activity_score"] for item in data["data"]]
            assert scores == sorted(scores, reverse=True)

    def test_bees_active_activity_asc_sort(self, test_client):
        """Test sorting by activity ascending."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=activity_asc")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            scores = [item["activity_score"] for item in data["data"]]
            assert scores == sorted(scores)

    def test_bees_active_peak_month_sort(self, test_client):
        """Test sorting by peak month."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=peak_month")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["sort"] == "peak_month"

    def test_bees_active_taxon_id_sort(self, test_client):
        """Test sorting by taxon_id."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=taxon_id")
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            taxon_ids = [item["taxon_id"] for item in data["data"]]
            assert taxon_ids == sorted(taxon_ids)

    def test_bees_active_research_grade(self, test_client):
        """Test require_research_grade parameter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&require_research_grade=true")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["require_research_grade"] is True

    def test_bees_active_absolute_activity(self, test_client):
        """Test absolute_activity parameter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&absolute_activity=false")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["absolute_activity"] is False

    def test_bees_active_min_activity(self, test_client):
        """Test min_activity filter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&min_activity=0.1")
        assert response.status_code == 200
        data = response.json()
        for item in data["data"]:
            assert item["activity_score"] >= 0.1

    def test_bees_active_candidate_cap(self, test_client):
        """Test candidate_cap parameter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&candidate_cap=100")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["candidate_cap"] == 100
        assert data["meta"]["candidate_count"] <= 100

    def test_bees_active_invalid_lat(self, test_client):
        """Test invalid latitude."""
        response = test_client.get("/bees/active?lat=100&lon=-122.4194")
        assert response.status_code == 422

    def test_bees_active_invalid_lon(self, test_client):
        """Test invalid longitude."""
        response = test_client.get("/bees/active?lat=37.7749&lon=200")
        assert response.status_code == 422

    def test_bees_active_invalid_date_format(self, test_client):
        """Test invalid date format."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&start_date=invalid")
        assert response.status_code == 422

    def test_bees_active_end_before_start(self, test_client):
        """Test end_date before start_date."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&start_date=2024-04-15&end_date=2024-04-01")
        assert response.status_code == 422
        assert "end_date must be >= start_date" in response.json()["detail"]

    def test_bees_active_window_too_large(self, test_client):
        """Test date window > 31 days."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&start_date=2024-04-01&end_date=2024-05-15")
        assert response.status_code == 422
        assert "Max window is 31 days" in response.json()["detail"]

    def test_bees_active_invalid_sort(self, test_client):
        """Test invalid sort parameter."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&sort=invalid")
        assert response.status_code == 422

    def test_bees_active_invalid_radius(self, test_client):
        """Test invalid radius (too large)."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&radius_km=250")
        assert response.status_code == 422

    def test_bees_active_invalid_limit(self, test_client):
        """Test invalid limit (too large)."""
        response = test_client.get("/bees/active?lat=37.7749&lon=-122.4194&limit=150")
        assert response.status_code == 422

    def test_bees_active_no_results_area(self, test_client):
        """Test area with no observations."""
        response = test_client.get("/bees/active?lat=0&lon=0&radius_km=1")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["count"] == 0
        assert data["meta"]["candidate_count"] == 0
        assert len(data["data"]) == 0


class TestBeesSearchEndpoint:
    """Tests for /bees/search endpoint."""

    def test_bees_search_basic(self, test_client):
        """Test basic search with common term."""
        response = test_client.get("/bees/search?q=bee")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "query" in data
        assert "count" in data
        assert data["query"] == "bee"
        assert isinstance(data["data"], list)

    def test_bees_search_scientific_name(self, test_client):
        """Test search with scientific name."""
        response = test_client.get("/bees/search?q=bombus")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    def test_bees_search_with_limit(self, test_client):
        """Test limit parameter."""
        response = test_client.get("/bees/search?q=bee&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_bees_search_min_length(self, test_client):
        """Test minimum query length validation."""
        response = test_client.get("/bees/search?q=a")
        assert response.status_code == 422

    def test_bees_search_invalid_limit(self, test_client):
        """Test invalid limit parameter."""
        response = test_client.get("/bees/search?q=bee&limit=150")
        assert response.status_code == 422

    def test_bees_search_no_query(self, test_client):
        """Test missing query parameter."""
        response = test_client.get("/bees/search")
        assert response.status_code == 422

    def test_bees_search_result_fields(self, test_client):
        """Test that results contain expected fields."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        data = response.json()
        if data["data"]:
            item = data["data"][0]
            assert "taxon_id" in item
            assert "scientific_name" in item
            assert "score" in item


class TestBeesPhenologyChartEndpoint:
    """Tests for /bees/phenology-chart/{taxon_id} endpoint."""

    def test_phenology_chart_valid_taxon(self, test_client):
        """Test chart generation for a valid taxon."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            assert "X-Phenology-Summary" in response.headers

    def test_phenology_chart_invalid_taxon(self, test_client):
        """Test chart generation for invalid taxon_id."""
        response = test_client.get("/bees/phenology-chart/999999999")
        assert response.status_code == 404
        assert "Taxon not found" in response.json()["detail"]

    def test_phenology_chart_with_params(self, test_client):
        """Test chart with custom parameters."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?width=800&height=600&highlight_window=false")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

    def test_phenology_chart_research_grade(self, test_client):
        """Test chart with require_research_grade."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?require_research_grade=true")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

    def test_phenology_chart_invalid_width(self, test_client):
        """Test invalid width parameter."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?width=100")
            assert response.status_code == 422

    def test_phenology_chart_invalid_height(self, test_client):
        """Test invalid height parameter."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?height=100")
            assert response.status_code == 422

    def test_phenology_chart_no_highlight_window(self, test_client):
        """Test chart without highlight window."""
        response = test_client.get("/bees/search?q=bee&limit=1")
        assert response.status_code == 200
        search_data = response.json()
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}?highlight_window=false")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"


class TestTripsCreateEndpoint:
    """Tests for POST /trips endpoint."""

    def test_create_trip_minimal(self, test_client):
        """Test creating a trip with minimal required fields."""
        import uuid

        event_name = f"Test Event {uuid.uuid4().hex[:8]}"
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": "John Doe"}],
            "start_time": "2025-05-01T09:00:00",
            "end_time": "2025-05-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["event_name"] == event_name
        assert len(data["organizers"]) == 1
        assert data["organizers"][0]["original"] == "John Doe"

    def test_create_trip_full(self, test_client):
        """Test creating a trip with all fields."""
        import uuid

        event_name = f"Full Test Event {uuid.uuid4().hex[:8]}"
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": "Jane Doe", "role": "Lead"}],
            "address_text": "123 Main St\nSan Francisco, CA",
            "country_hint": "US",
            "start_time": "2025-06-01T09:00:00",
            "end_time": "2025-06-01T17:00:00",
            "approx_latitude": 37.7749,
            "approx_longitude": -122.4194,
            "positional_accuracy_m": 100,
            "contact_emails": ["test@example.com"],
            "notes": "This is a test note",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["event_name"] == event_name
        assert data["location"]["approx_latitude"] == 37.7749
        assert data["address"]["country"] == "US"
        assert data["notes_sanitized"] == "This is a test note"

    def test_create_trip_multiple_organizers(self, test_client):
        """Test creating a trip with multiple organizers."""
        import uuid

        event_name = f"Multi-Organizer Event {uuid.uuid4().hex[:8]}"
        payload = {
            "event_name": event_name,
            "organizers": [
                {"display_name": "Alice", "role": "Lead"},
                {"display_name": "Bob", "role": "Assistant"},
            ],
            "start_time": "2025-07-01T09:00:00",
            "end_time": "2025-07-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["organizers"]) == 2

    def test_create_trip_diacritics_organizer(self, test_client):
        """Test organizer name with diacritics (combining marks)."""
        import unicodedata
        import uuid

        event_name = f"Diacritics Test {uuid.uuid4().hex[:8]}"
        # Use NFD normalization to create name with combining diacritics
        name_with_diacritics = unicodedata.normalize("NFD", "José García")
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": name_with_diacritics}],
            "start_time": "2025-08-01T09:00:00",
            "end_time": "2025-08-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        # The original should match what we sent
        assert data["organizers"][0]["original"] == name_with_diacritics
        # Should detect diacritics when using NFD normalization
        assert data["organizers"][0]["has_diacritics"] is True
        # The normalized version should have diacritics removed
        assert data["organizers"][0]["normalized"] != name_with_diacritics

    def test_create_trip_sanitize_notes(self, test_client):
        """Test notes sanitization removes script tags."""
        import uuid

        event_name = f"Sanitize Test {uuid.uuid4().hex[:8]}"
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2025-09-01T09:00:00",
            "end_time": "2025-09-01T17:00:00",
            "notes": "Safe text <script>alert('xss')</script> more text",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "script" not in data["notes_sanitized"].lower()
        assert "Safe text" in data["notes_sanitized"]
        assert "notes: script/style tags removed" in data["warnings"]

    def test_create_trip_invalid_timestamps(self, test_client):
        """Test invalid timestamp format."""
        payload = {
            "event_name": "Invalid Time",
            "organizers": [{"display_name": "Test User"}],
            "start_time": "invalid",
            "end_time": "2025-05-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422

    def test_create_trip_end_before_start(self, test_client):
        """Test end_time before start_time."""
        payload = {
            "event_name": "Bad Times",
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2025-05-01T17:00:00",
            "end_time": "2025-05-01T09:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "end_time must be > start_time" in response.json()["detail"]

    def test_create_trip_duration_too_long(self, test_client):
        """Test duration > 24 hours."""
        payload = {
            "event_name": "Too Long",
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2025-05-01T09:00:00",
            "end_time": "2025-05-02T10:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "Duration must be <= 24h" in response.json()["detail"]

    def test_create_trip_no_organizers(self, test_client):
        """Test creating trip without organizers."""
        payload = {
            "event_name": "No Organizers",
            "organizers": [],
            "start_time": "2025-05-01T09:00:00",
            "end_time": "2025-05-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "At least one organizer required" in response.json()["detail"]

    def test_create_trip_empty_organizer_names(self, test_client):
        """Test organizers with empty display names."""
        payload = {
            "event_name": "Empty Names",
            "organizers": [{"display_name": "  "}],
            "start_time": "2025-05-01T09:00:00",
            "end_time": "2025-05-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "No valid organizers provided" in response.json()["detail"]

    def test_create_trip_slug_generation(self, test_client):
        """Test event slug generation."""
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        event_name = f"Test Event 123 {unique_id}!"
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2025-05-01T09:00:00",
            "end_time": "2025-05-01T17:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        # Check that slug is generated correctly (lowercased, special chars removed)
        assert unique_id in data["event_slug"]
        assert "!" not in data["event_slug"]


class TestTripsGetEndpoint:
    """Tests for GET /trips/{trip_id} endpoint."""

    def test_get_trip_existing(self, test_client):
        """Test retrieving an existing trip."""
        import uuid

        event_name = f"Retrieve Test {uuid.uuid4().hex[:8]}"
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2025-05-01T09:00:00",
            "end_time": "2025-05-01T17:00:00",
        }
        create_response = test_client.post("/trips", json=payload)
        assert create_response.status_code == 201
        trip_id = create_response.json()["id"]

        response = test_client.get(f"/trips/{trip_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == trip_id
        assert data["event_name"] == event_name

    def test_get_trip_not_found(self, test_client):
        """Test retrieving non-existent trip."""
        response = test_client.get("/trips/999999999")
        assert response.status_code == 404
        assert "Trip not found" in response.json()["detail"]


class TestTripsListEndpoint:
    """Tests for GET /trips endpoint."""

    def test_list_trips_all(self, test_client):
        """Test listing all trips."""
        response = test_client.get("/trips")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)

    def test_list_trips_with_since(self, test_client):
        """Test filtering trips with since parameter."""
        import uuid

        event_name = f"Future Event {uuid.uuid4().hex[:8]}"
        payload = {
            "event_name": event_name,
            "organizers": [{"display_name": "Test User"}],
            "start_time": "2026-05-01T09:00:00",
            "end_time": "2026-05-01T17:00:00",
        }
        test_client.post("/trips", json=payload)

        response = test_client.get("/trips?since=2026-01-01")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["since"] == "2026-01-01"

    def test_list_trips_with_before(self, test_client):
        """Test filtering trips with before parameter."""
        response = test_client.get("/trips?before=2025-01-01")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["before"] == "2025-01-01"

    def test_list_trips_with_both_filters(self, test_client):
        """Test filtering trips with both since and before."""
        response = test_client.get("/trips?since=2025-01-01&before=2025-12-31")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["since"] == "2025-01-01"
        assert data["meta"]["query"]["before"] == "2025-12-31"

    def test_list_trips_invalid_since(self, test_client):
        """Test invalid since parameter."""
        response = test_client.get("/trips?since=invalid")
        assert response.status_code == 422
        assert "Invalid since date" in response.json()["detail"]

    def test_list_trips_invalid_before(self, test_client):
        """Test invalid before parameter."""
        response = test_client.get("/trips?before=invalid")
        assert response.status_code == 422
        assert "Invalid before date" in response.json()["detail"]
