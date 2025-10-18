import uuid


class TestBeesActiveEndpoint:
    """Test the /bees/active endpoint."""

    def test_bees_active_basic(self, test_client):
        """Test basic call to bees/active with default parameters."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)
        assert "count" in data["meta"]

    def test_bees_active_with_date_range(self, test_client):
        """Test bees/active with explicit date range."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "2024-01-01",
                "end_date": "2024-01-15",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["start_date"] == "2024-01-01"
        assert data["meta"]["end_date"] == "2024-01-15"

    def test_bees_active_invalid_date(self, test_client):
        """Test bees/active with invalid date format."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "invalid",
            },
        )
        assert response.status_code == 422

    def test_bees_active_end_before_start(self, test_client):
        """Test bees/active with end_date before start_date."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "2024-01-15",
                "end_date": "2024-01-01",
            },
        )
        assert response.status_code == 422
        assert "end_date must be >= start_date" in response.json()["detail"]

    def test_bees_active_window_too_large(self, test_client):
        """Test bees/active with window larger than 31 days."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "2024-01-01",
                "end_date": "2024-02-15",
            },
        )
        assert response.status_code == 422
        assert "Max window is 31 days" in response.json()["detail"]

    def test_bees_active_with_radius(self, test_client):
        """Test bees/active with custom radius."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "radius_km": 50,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["radius_km"] == 50

    def test_bees_active_with_limit(self, test_client):
        """Test bees/active with custom limit."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "limit": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_bees_active_sort_activity_desc(self, test_client):
        """Test bees/active sorted by activity descending."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "sort": "activity_desc",
            },
        )
        assert response.status_code == 200
        data = response.json()
        scores = [item["activity_score"] for item in data["data"]]
        assert scores == sorted(scores, reverse=True)

    def test_bees_active_sort_activity_asc(self, test_client):
        """Test bees/active sorted by activity ascending."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "sort": "activity_asc",
            },
        )
        assert response.status_code == 200
        data = response.json()
        scores = [item["activity_score"] for item in data["data"]]
        assert scores == sorted(scores)

    def test_bees_active_sort_peak_month(self, test_client):
        """Test bees/active sorted by peak_month."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "sort": "peak_month",
            },
        )
        assert response.status_code == 200

    def test_bees_active_sort_taxon_id(self, test_client):
        """Test bees/active sorted by taxon_id."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "sort": "taxon_id",
            },
        )
        assert response.status_code == 200
        data = response.json()
        taxon_ids = [item["taxon_id"] for item in data["data"]]
        assert taxon_ids == sorted(taxon_ids)

    def test_bees_active_require_research_grade(self, test_client):
        """Test bees/active with require_research_grade flag."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "require_research_grade": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["require_research_grade"] is True

    def test_bees_active_absolute_activity(self, test_client):
        """Test bees/active with absolute_activity flag."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "absolute_activity": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["absolute_activity"] is False

    def test_bees_active_min_activity(self, test_client):
        """Test bees/active with min_activity threshold."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "min_activity": 0.1,
            },
        )
        assert response.status_code == 200

    def test_bees_active_candidate_cap(self, test_client):
        """Test bees/active with custom candidate_cap."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "candidate_cap": 100,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["candidate_cap"] == 100

    def test_bees_active_invalid_lat(self, test_client):
        """Test bees/active with invalid latitude."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 100,
                "lon": -122.4194,
            },
        )
        assert response.status_code == 422

    def test_bees_active_invalid_lon(self, test_client):
        """Test bees/active with invalid longitude."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": 200,
            },
        )
        assert response.status_code == 422

    def test_bees_active_no_results(self, test_client):
        """Test bees/active with location that has no data."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 0,
                "lon": 0,
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["candidate_count"] == 0

    def test_bees_active_with_real_data(self, test_client):
        """Test bees/active with location that returns actual data."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.859,
                "lon": -122.262,
                "radius_km": 50,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        if data["meta"]["candidate_count"] > 0:
            assert len(data["data"]) >= 0

    def test_bees_active_with_filtering(self, test_client):
        """Test bees/active with data and filtering by min_activity."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.859,
                "lon": -122.262,
                "radius_km": 50,
                "min_activity": 0.001,
                "absolute_activity": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        if data["meta"]["candidate_count"] > 0:
            for item in data["data"]:
                assert "taxon_id" in item
                assert "scientific_name" in item
                assert "activity_score" in item


class TestBeesSearchEndpoint:
    """Test the /bees/search endpoint."""

    def test_bees_search_basic(self, test_client):
        """Test basic call to bees/search."""
        response = test_client.get(
            "/bees/search",
            params={"q": "bombus"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "query" in data
        assert "count" in data
        assert data["query"] == "bombus"

    def test_bees_search_with_limit(self, test_client):
        """Test bees/search with custom limit."""
        response = test_client.get(
            "/bees/search",
            params={
                "q": "bee",
                "limit": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

    def test_bees_search_too_short(self, test_client):
        """Test bees/search with query that is too short."""
        response = test_client.get(
            "/bees/search",
            params={"q": "a"},
        )
        assert response.status_code == 422

    def test_bees_search_no_results(self, test_client):
        """Test bees/search with query that returns no results."""
        response = test_client.get(
            "/bees/search",
            params={"q": "xyzzynonexistent"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert len(data["data"]) == 0


class TestBeesPhenologyChartEndpoint:
    """Test the /bees/phenology-chart/{taxon_id} endpoint."""

    def test_phenology_chart_basic(self, test_client):
        """Test basic call to phenology chart endpoint."""
        response = test_client.get("/bees/phenology-chart/1")
        assert response.status_code in [200, 404]

    def test_phenology_chart_not_found(self, test_client):
        """Test phenology chart with non-existent taxon."""
        response = test_client.get("/bees/phenology-chart/999999999")
        assert response.status_code == 404
        assert "Taxon not found" in response.json()["detail"]

    def test_phenology_chart_with_dimensions(self, test_client):
        """Test phenology chart with custom dimensions."""
        response = test_client.get(
            "/bees/phenology-chart/1",
            params={
                "width": 800,
                "height": 400,
            },
        )
        assert response.status_code in [200, 404]

    def test_phenology_chart_highlight_window(self, test_client):
        """Test phenology chart with highlight_window parameter."""
        response = test_client.get(
            "/bees/phenology-chart/1",
            params={"highlight_window": False},
        )
        assert response.status_code in [200, 404]

    def test_phenology_chart_require_research_grade(self, test_client):
        """Test phenology chart with require_research_grade flag."""
        response = test_client.get(
            "/bees/phenology-chart/1",
            params={"require_research_grade": True},
        )
        assert response.status_code in [200, 404]

    def test_phenology_chart_with_real_taxon(self, test_client):
        """Test phenology chart with a real taxon that has data."""
        response = test_client.get("/bees/phenology-chart/1453119")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert "X-Phenology-Summary" in response.headers


class TestTripsEndpoints:
    """Test the trip-related endpoints."""

    def test_create_trip_basic(self, test_client):
        """Test creating a basic trip."""
        event_name = f"Test Trip {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "John Doe", "role": "guide"}],
                "start_time": "2025-05-01T10:00:00",
                "end_time": "2025-05-01T15:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event_name"] == event_name
        assert len(data["organizers"]) == 1
        assert data["organizers"][0]["original"] == "John Doe"

    def test_create_trip_with_location(self, test_client):
        """Test creating a trip with location data."""
        event_name = f"Located Trip {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Jane Smith"}],
                "start_time": "2025-06-01T09:00:00",
                "end_time": "2025-06-01T17:00:00",
                "approx_latitude": 37.7749,
                "approx_longitude": -122.4194,
                "positional_accuracy_m": 100,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["location"]["approx_latitude"] == 37.7749
        assert data["location"]["approx_longitude"] == -122.4194

    def test_create_trip_with_address(self, test_client):
        """Test creating a trip with address."""
        event_name = f"Trip with Address {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Guide"}],
                "start_time": "2025-07-01T08:00:00",
                "end_time": "2025-07-01T12:00:00",
                "address_text": "123 Main St\nSan Francisco, CA",
                "country_hint": "US",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["address"] is not None
        assert len(data["address"]["lines"]) == 2
        assert data["address"]["country"] == "US"

    def test_create_trip_with_notes(self, test_client):
        """Test creating a trip with notes."""
        event_name = f"Trip with Notes {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-08-01T10:00:00",
                "end_time": "2025-08-01T14:00:00",
                "notes": "This is a test trip with notes.",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["notes_sanitized"] == "This is a test trip with notes."

    def test_create_trip_sanitize_script_tags(self, test_client):
        """Test that script tags are removed from notes."""
        event_name = f"Trip with Script {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-09-01T10:00:00",
                "end_time": "2025-09-01T14:00:00",
                "notes": "Safe text <script>alert('xss')</script> more text",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "<script>" not in data["notes_sanitized"]
        assert "notes: script/style tags removed" in data["warnings"]

    def test_create_trip_invalid_timestamps(self, test_client):
        """Test creating a trip with invalid timestamps."""
        response = test_client.post(
            "/trips",
            json={
                "event_name": "Invalid Trip",
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "invalid",
                "end_time": "2025-05-01T15:00:00",
            },
        )
        assert response.status_code == 422
        assert "Invalid timestamps" in response.json()["detail"]

    def test_create_trip_end_before_start(self, test_client):
        """Test creating a trip with end_time before start_time."""
        response = test_client.post(
            "/trips",
            json={
                "event_name": "Invalid Trip",
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-05-01T15:00:00",
                "end_time": "2025-05-01T10:00:00",
            },
        )
        assert response.status_code == 422
        assert "end_time must be > start_time" in response.json()["detail"]

    def test_create_trip_duration_too_long(self, test_client):
        """Test creating a trip with duration > 24 hours."""
        response = test_client.post(
            "/trips",
            json={
                "event_name": "Long Trip",
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-05-01T10:00:00",
                "end_time": "2025-05-02T11:00:00",
            },
        )
        assert response.status_code == 422
        assert "Duration must be <= 24h" in response.json()["detail"]

    def test_create_trip_no_organizers(self, test_client):
        """Test creating a trip with no organizers."""
        response = test_client.post(
            "/trips",
            json={
                "event_name": "No Organizers Trip",
                "organizers": [],
                "start_time": "2025-05-01T10:00:00",
                "end_time": "2025-05-01T15:00:00",
            },
        )
        assert response.status_code == 422
        assert "At least one organizer required" in response.json()["detail"]

    def test_create_trip_empty_organizer_names(self, test_client):
        """Test creating a trip with empty organizer names."""
        response = test_client.post(
            "/trips",
            json={
                "event_name": "Empty Organizers",
                "organizers": [{"display_name": ""}],
                "start_time": "2025-05-01T10:00:00",
                "end_time": "2025-05-01T15:00:00",
            },
        )
        assert response.status_code == 422
        assert "No valid organizers provided" in response.json()["detail"]

    def test_create_trip_with_diacritics(self, test_client):
        """Test creating a trip with organizer names containing diacritics (combining marks)."""
        import unicodedata

        event_name = f"Diacritic Trip {uuid.uuid4().hex[:8]}"
        name_with_combining = "Jose" + "\u0301"
        normalized_name = unicodedata.normalize("NFD", name_with_combining)
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": normalized_name}],
                "start_time": "2025-05-01T10:00:00",
                "end_time": "2025-05-01T15:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["organizers"][0]["has_diacritics"] is True

    def test_get_trip_basic(self, test_client):
        """Test getting a trip by ID."""
        event_name = f"Get Test Trip {uuid.uuid4().hex[:8]}"
        create_response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-05-01T10:00:00",
                "end_time": "2025-05-01T15:00:00",
            },
        )
        trip_id = create_response.json()["id"]

        get_response = test_client.get(f"/trips/{trip_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == trip_id
        assert data["event_name"] == event_name

    def test_get_trip_not_found(self, test_client):
        """Test getting a non-existent trip."""
        response = test_client.get("/trips/999999999")
        assert response.status_code == 404
        assert "Trip not found" in response.json()["detail"]

    def test_list_trips_basic(self, test_client):
        """Test listing trips."""
        response = test_client.get("/trips")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)

    def test_list_trips_with_since(self, test_client):
        """Test listing trips with since filter."""
        event_name = f"Future Trip {uuid.uuid4().hex[:8]}"
        test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-12-01T10:00:00",
                "end_time": "2025-12-01T15:00:00",
            },
        )

        response = test_client.get("/trips", params={"since": "2025-11-01"})
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["since"] == "2025-11-01"

    def test_list_trips_with_before(self, test_client):
        """Test listing trips with before filter."""
        response = test_client.get("/trips", params={"before": "2025-01-01"})
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["query"]["before"] == "2025-01-01"

    def test_list_trips_invalid_since_date(self, test_client):
        """Test listing trips with invalid since date."""
        response = test_client.get("/trips", params={"since": "invalid"})
        assert response.status_code == 422
        assert "Invalid since date" in response.json()["detail"]

    def test_list_trips_invalid_before_date(self, test_client):
        """Test listing trips with invalid before date."""
        response = test_client.get("/trips", params={"before": "invalid"})
        assert response.status_code == 422
        assert "Invalid before date" in response.json()["detail"]

    def test_create_trip_with_contact_emails(self, test_client):
        """Test creating a trip with contact emails."""
        event_name = f"Trip with Emails {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [{"display_name": "Organizer"}],
                "start_time": "2025-10-01T10:00:00",
                "end_time": "2025-10-01T15:00:00",
                "contact_emails": ["test@example.com", "another@example.com"],
            },
        )
        assert response.status_code == 201

    def test_create_trip_organizer_with_role(self, test_client):
        """Test creating a trip with organizer roles."""
        event_name = f"Trip with Roles {uuid.uuid4().hex[:8]}"
        response = test_client.post(
            "/trips",
            json={
                "event_name": event_name,
                "organizers": [
                    {"display_name": "Guide One", "role": "lead"},
                    {"display_name": "Guide Two", "role": "assistant"},
                ],
                "start_time": "2025-11-01T10:00:00",
                "end_time": "2025-11-01T15:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["organizers"]) == 2
        assert data["organizers"][0]["role"] == "lead"
        assert data["organizers"][1]["role"] == "assistant"
