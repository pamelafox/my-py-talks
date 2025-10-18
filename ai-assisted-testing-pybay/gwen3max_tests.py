"""
============================================ tests coverage =============================================
___________________________ coverage: platform linux, python 3.12.11-final-0 ____________________________

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/backend/fastapi_app/api/models.py      67      0   100%
src/backend/fastapi_app/api/routes.py     190     94    51%   34-35, 128-151, 154-172, 174, 176, 178, 180-181, 236-251, 277-318, 320, 322, 325-349, 386, 398, 406-409, 429-431, 461-464, 501, 507, 511-512
---------------------------------------------------------------------
TOTAL                                     257     94    63%
======================================== short test summary info ========================================
FAILED tests/test_routes.py::TestTripEndpoints::test_create_trip_success - sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'async...
FAILED tests/test_routes.py::TestTripEndpoints::test_get_trip_success - sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'async...
FAILED tests/test_routes.py::TestTripEndpoints::test_list_trips_with_filters - sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'async...
===================================== 3 failed, 20 passed in 5.91s ======================================
"""
from fastapi.testclient import TestClient


class TestBeeActivityEndpoints:
    """Tests for bee activity endpoints."""

    def test_bees_active_success(self, test_client: TestClient):
        """Test successful bee activity query with default parameters."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)
        assert isinstance(data["meta"], dict)
        assert data["meta"]["lat"] == 37.7749
        assert data["meta"]["lon"] == -122.4194

    def test_bees_active_with_custom_dates(self, test_client: TestClient):
        """Test bee activity query with custom date range."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["start_date"] == "2025-01-01"
        assert data["meta"]["end_date"] == "2025-01-31"
        assert data["meta"]["defaulted_dates"] is False

    def test_bees_active_invalid_date_range(self, test_client: TestClient):
        """Test bee activity query with invalid date range (end before start)."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "2025-01-31",
                "end_date": "2025-01-01",
            }
        )
        assert response.status_code == 422
        assert "end_date must be >= start_date" in response.json()["detail"]

    def test_bees_active_window_too_large(self, test_client: TestClient):
        """Test bee activity query with window larger than 31 days."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "start_date": "2025-01-01",
                "end_date": "2025-02-15",  # 45 days
            }
        )
        assert response.status_code == 422
        assert "Max window is 31 days" in response.json()["detail"]

    def test_bees_active_invalid_coordinates(self, test_client: TestClient):
        """Test bee activity query with invalid coordinates."""
        # Test latitude out of bounds
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 91.0,  # Invalid latitude
                "lon": -122.4194,
            }
        )
        assert response.status_code == 422

        # Test longitude out of bounds
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": 181.0,  # Invalid longitude
            }
        )
        assert response.status_code == 422

    def test_bees_active_with_sorting(self, test_client: TestClient):
        """Test bee activity query with different sort options."""
        sort_options = ["activity_desc", "activity_asc", "peak_month", "taxon_id"]
        for sort_option in sort_options:
            response = test_client.get(
                "/bees/active",
                params={
                    "lat": 37.7749,
                    "lon": -122.4194,
                    "sort": sort_option,
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["meta"]["sort"] == sort_option

    def test_bees_active_invalid_sort(self, test_client: TestClient):
        """Test bee activity query with invalid sort option."""
        response = test_client.get(
            "/bees/active",
            params={
                "lat": 37.7749,
                "lon": -122.4194,
                "sort": "invalid_sort",
            }
        )
        assert response.status_code == 422


class TestSpeciesSearchEndpoints:
    """Tests for species search endpoints."""

    def test_bees_search_success(self, test_client: TestClient):
        """Test successful species search."""
        response = test_client.get(
            "/bees/search",
            params={"q": "apis"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "count" in data
        assert "data" in data
        assert data["query"] == "apis"
        assert isinstance(data["data"], list)

    def test_bees_search_min_length(self, test_client: TestClient):
        """Test species search with query too short."""
        response = test_client.get(
            "/bees/search",
            params={"q": "a"}  # Less than 2 characters
        )
        assert response.status_code == 422

    def test_bees_search_with_limit(self, test_client: TestClient):
        """Test species search with custom limit."""
        response = test_client.get(
            "/bees/search",
            params={"q": "apis", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 10


class TestPhenologyChartEndpoints:
    """Tests for phenology chart endpoints."""

    def test_bees_phenology_chart_success(self, test_client: TestClient):
        """Test successful phenology chart generation."""
        # First, get a valid taxon_id from the database
        search_response = test_client.get("/bees/search", params={"q": "apis"})
        assert search_response.status_code == 200
        search_data = search_response.json()
        
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(f"/bees/phenology-chart/{taxon_id}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            assert "X-Phenology-Summary" in response.headers

    def test_bees_phenology_chart_not_found(self, test_client: TestClient):
        """Test phenology chart with invalid taxon_id."""
        response = test_client.get("/bees/phenology-chart/999999")
        assert response.status_code == 404
        assert "Taxon not found" in response.json()["detail"]

    def test_bees_phenology_chart_with_research_grade(self, test_client: TestClient):
        """Test phenology chart with research grade flag."""
        search_response = test_client.get("/bees/search", params={"q": "apis"})
        assert search_response.status_code == 200
        search_data = search_response.json()
        
        if search_data["data"]:
            taxon_id = search_data["data"][0]["taxon_id"]
            response = test_client.get(
                f"/bees/phenology-chart/{taxon_id}",
                params={"require_research_grade": True}
            )
            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"


class TestTripEndpoints:
    """Tests for trip endpoints."""

    def test_create_trip_success(self, test_client: TestClient):
        """Test successful trip creation."""
        payload = {
            "event_name": "Test Bee Trip",
            "organizers": [{"display_name": "Test Organizer"}],
            "start_time": "2025-06-01T10:00:00",
            "end_time": "2025-06-01T12:00:00",
            "approx_latitude": 37.7749,
            "approx_longitude": -122.4194,
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["event_name"] == "Test Bee Trip"
        assert data["time_window"]["duration_hours"] == 2.0

    def test_create_trip_invalid_timestamps(self, test_client: TestClient):
        """Test trip creation with invalid timestamps."""
        payload = {
            "event_name": "Test Bee Trip",
            "organizers": [{"display_name": "Test Organizer"}],
            "start_time": "invalid",
            "end_time": "2025-06-01T12:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422

    def test_create_trip_end_before_start(self, test_client: TestClient):
        """Test trip creation with end time before start time."""
        payload = {
            "event_name": "Test Bee Trip",
            "organizers": [{"display_name": "Test Organizer"}],
            "start_time": "2025-06-01T12:00:00",
            "end_time": "2025-06-01T10:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "end_time must be > start_time" in response.json()["detail"]

    def test_create_trip_duration_too_long(self, test_client: TestClient):
        """Test trip creation with duration longer than 24 hours."""
        payload = {
            "event_name": "Test Bee Trip",
            "organizers": [{"display_name": "Test Organizer"}],
            "start_time": "2025-06-01T10:00:00",
            "end_time": "2025-06-02T11:00:00",  # 25 hours
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "Duration must be <= 24h" in response.json()["detail"]

    def test_create_trip_no_organizers(self, test_client: TestClient):
        """Test trip creation with no organizers."""
        payload = {
            "event_name": "Test Bee Trip",
            "organizers": [],
            "start_time": "2025-06-01T10:00:00",
            "end_time": "2025-06-01T12:00:00",
        }
        response = test_client.post("/trips", json=payload)
        assert response.status_code == 422
        assert "At least one organizer required" in response.json()["detail"]

    def test_get_trip_success(self, test_client: TestClient):
        """Test successful trip retrieval."""
        # First create a trip
        create_payload = {
            "event_name": "Test Bee Trip for Get",
            "organizers": [{"display_name": "Test Organizer"}],
            "start_time": "2025-06-01T10:00:00",
            "end_time": "2025-06-01T12:00:00",
        }
        create_response = test_client.post("/trips", json=create_payload)
        assert create_response.status_code == 201
        trip_id = create_response.json()["id"]

        # Then retrieve it
        response = test_client.get(f"/trips/{trip_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == trip_id
        assert data["event_name"] == "Test Bee Trip for Get"

    def test_get_trip_not_found(self, test_client: TestClient):
        """Test trip retrieval with invalid ID."""
        response = test_client.get("/trips/999999")
        assert response.status_code == 404
        assert "Trip not found" in response.json()["detail"]

    def test_list_trips_success(self, test_client: TestClient):
        """Test successful trip listing."""
        response = test_client.get("/trips")
        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_list_trips_with_filters(self, test_client: TestClient):
        """Test trip listing with date filters."""
        # Create a trip for testing
        create_payload = {
            "event_name": "Filtered Test Trip",
            "organizers": [{"display_name": "Test Organizer"}],
            "start_time": "2025-06-01T10:00:00",
            "end_time": "2025-06-01T12:00:00",
        }
        test_client.post("/trips", json=create_payload)

        # Test since filter
        response = test_client.get("/trips", params={"since": "2025-05-01"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0

        # Test before filter
        response = test_client.get("/trips", params={"before": "2025-07-01"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0

    def test_list_trips_invalid_dates(self, test_client: TestClient):
        """Test trip listing with invalid date filters."""
        response = test_client.get("/trips", params={"since": "invalid-date"})
        assert response.status_code == 422

        response = test_client.get("/trips", params={"before": "invalid-date"})
        assert response.status_code == 422