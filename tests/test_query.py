import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from ingest.app import app as ingest_app
from query.app import app as query_app

ingest_client = TestClient(ingest_app)
query_client = TestClient(query_app)


# ------------------------
# Test Setup: Seed Data with Specific Timestamps
# ------------------------

@pytest.fixture(scope="function")
def seed_data():
    """Seed test data with known timestamps for isolation."""
    # Use a specific date for this test run (midnight for clean date filtering)
    test_date = datetime(2024, 1, 15, 0, 0, 0)
    
    payloads = [
        {
            "sensor_id": 1,
            "metric_type": "temperature",
            "value": 20,
            "timestamp": test_date.isoformat(),
        },
        {
            "sensor_id": 1,
            "metric_type": "temperature",
            "value": 24,
            "timestamp": (test_date + timedelta(hours=1)).isoformat(),
        },
        {
            "sensor_id": 1,
            "metric_type": "humidity",
            "value": 50,
            "timestamp": test_date.isoformat(),
        },
        {
            "sensor_id": 2,
            "metric_type": "temperature",
            "value": 30,
            "timestamp": test_date.isoformat(),
        },
    ]

    for payload in payloads:
        response = ingest_client.post("/metrics", json=payload)
        assert response.status_code == 201
    
    return test_date


# ------------------------
# Valid Query Tests
# ------------------------

def test_query_avg_temperature_single_sensor(seed_data):
    test_date = seed_data
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["statistic"] == "avg"
    assert body["results"]["1"]["temperature"] == 22.0


def test_query_multiple_metrics(seed_data):
    test_date = seed_data
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature,humidity",
            "statistic": "avg",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["results"]["1"]["temperature"] == 22.0
    assert body["results"]["1"]["humidity"] == 50.0


def test_query_all_sensors_max_temperature(seed_data):
    test_date = seed_data
    response = query_client.get(
        "/query",
        params={
            "sensors": "all",
            "metrics": "temperature",
            "statistic": "max",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["results"]["1"]["temperature"] == 24.0
    assert body["results"]["2"]["temperature"] == 30.0


# ------------------------
# Empty Result Test
# ------------------------

def test_query_no_matching_data_returns_empty_results():
    # Query a date with no data
    response = query_client.get(
        "/query",
        params={
            "sensors": "999",
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": "2099-12-31",
            "end_date": "2099-12-31",
        },
    )

    assert response.status_code == 200
    assert response.json()["results"] == {}


# ------------------------
# Invalid Input Tests
# ------------------------

@pytest.mark.parametrize(
    "params",
    [
        {
            "sensors": "abc",
            "metrics": "temperature",
            "statistic": "avg",
        },  # invalid sensor ids
        {
            "sensors": "1",
            "metrics": "",
            "statistic": "avg",
        },  # empty metrics
    ],
)
def test_query_invalid_parameters(params):
    response = query_client.get("/query", params=params)
    assert response.status_code in (400, 422)


def test_query_invalid_statistic():
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature",
            "statistic": "median",
        },
    )

    assert response.status_code == 422
