from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(taxon_id=st.integers())
def test_phenology_chart_any_integer(test_client, taxon_id: int):
    response = test_client.get(f"/bees/phenology-chart/{taxon_id}")
    assert response.status_code in (200, 404)


@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    lat=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
    min_act=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_bees_active_scores_property(test_client, lat: float, lon: float, min_act: float) -> None:
    """Property-based: normalized mode scores stay within [0,1] and meet the threshold.

    Invariants:
    * meta.count == len(data)
    * 0 <= activity_score <= 1
    * activity_score >= min_activity
    """
    response = test_client.get(
        "/bees/active",
        params={
            "lat": lat,
            "lon": lon,
            "absolute_activity": False,
            "min_activity": min_act,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["count"] == len(payload["data"])
    for item in payload["data"]:
        score = item["activity_score"]
        assert 0.0 <= score <= 1.0
        assert score >= min_act
