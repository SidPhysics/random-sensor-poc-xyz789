import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import uuid

from ingest.app import app as ingest_app
from query.app import app as query_app

ingest_client = TestClient(ingest_app)
query_client = TestClient(query_app)


# ------------------------
# Test Setup: UUID-based Unique Sensor IDs
# ------------------------


@pytest.fixture
def unique_sensor_id():
    """Generate unique sensor ID using UUID to avoid test interference."""
    return int(str(uuid.uuid4().int)[:8])


@pytest.fixture
def seed_data(unique_sensor_id):
    """Seed test data with unique sensor ID for isolation."""
    test_date = datetime(2024, 1, 15, 0, 0, 0)

    payloads = [
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 20,
            "timestamp": test_date.isoformat(),
        },
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 24,
            "timestamp": (test_date + timedelta(hours=1)).isoformat(),
        },
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "humidity",
            "value": 50,
            "timestamp": test_date.isoformat(),
        },
    ]

    for payload in payloads:
        response = ingest_client.post("/metrics", json=payload)
        assert response.status_code == 201

    return {"test_date": test_date, "sensor_id": unique_sensor_id}


# ------------------------
# Latest Data Query Tests (No Date Range)
# ------------------------


def test_query_latest_temperature_single_sensor(seed_data):
    """Test latest data query returns most recent value with timestamp."""
    sensor_id = seed_data["sensor_id"]
    response = query_client.get(
        "/query",
        params={
            "sensors": str(sensor_id),
            "metrics": "temperature",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["statistic"] == "latest"
    assert body["results"][str(sensor_id)]["temperature"] == 24  # Latest value
    assert "ingested_at" in body["results"][str(sensor_id)]


def test_query_latest_multiple_metrics(seed_data):
    """Test latest data query with multiple metrics."""
    sensor_id = seed_data["sensor_id"]
    response = query_client.get(
        "/query",
        params={
            "sensors": str(sensor_id),
            "metrics": "temperature,humidity",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["results"][str(sensor_id)]["temperature"] == 24  # Latest temperature
    assert body["results"][str(sensor_id)]["humidity"] == 50  # Latest humidity
    assert "ingested_at" in body["results"][str(sensor_id)]


def test_query_latest_all_sensors(unique_sensor_id):
    """Test latest data query for all sensors."""
    # Create data for this specific test
    test_date = datetime(2024, 1, 15, 0, 0, 0)
    payloads = [
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 25,
            "timestamp": test_date.isoformat(),
        },
    ]

    for payload in payloads:
        response = ingest_client.post("/metrics", json=payload)
        assert response.status_code == 201

    response = query_client.get(
        "/query",
        params={
            "sensors": "all",
            "metrics": "temperature",
        },
    )

    assert response.status_code == 200
    body = response.json()

    # Should contain our sensor among others
    assert str(unique_sensor_id) in body["results"]
    assert body["results"][str(unique_sensor_id)]["temperature"] == 25
    assert "ingested_at" in body["results"][str(unique_sensor_id)]


# ------------------------
# Date Range Query Tests (Aggregated)
# ------------------------


def test_query_avg_temperature_single_sensor(seed_data):
    """Test aggregated query with date range."""
    test_date = seed_data["test_date"]
    sensor_id = seed_data["sensor_id"]
    response = query_client.get(
        "/query",
        params={
            "sensors": str(sensor_id),
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["statistic"] == "avg"
    assert body["results"][str(sensor_id)]["temperature"] == 22.0
    assert (
        "ingested_at" not in body["results"][str(sensor_id)]
    )  # No timestamp for aggregated queries


def test_query_multiple_metrics(seed_data):
    """Test aggregated query with multiple metrics and date range."""
    test_date = seed_data["test_date"]
    sensor_id = seed_data["sensor_id"]
    response = query_client.get(
        "/query",
        params={
            "sensors": str(sensor_id),
            "metrics": "temperature,humidity",
            "statistic": "avg",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["results"][str(sensor_id)]["temperature"] == 22.0
    assert body["results"][str(sensor_id)]["humidity"] == 50.0
    assert "ingested_at" not in body["results"][str(sensor_id)]


def test_query_all_sensors_max_temperature(unique_sensor_id):
    """Test aggregated query for max temperature."""
    test_date = datetime(2024, 1, 15, 0, 0, 0)
    payloads = [
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 30,
            "timestamp": test_date.isoformat(),
        },
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 35,
            "timestamp": (test_date + timedelta(hours=1)).isoformat(),
        },
    ]

    for payload in payloads:
        response = ingest_client.post("/metrics", json=payload)
        assert response.status_code == 201

    response = query_client.get(
        "/query",
        params={
            "sensors": str(unique_sensor_id),
            "metrics": "temperature",
            "statistic": "max",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["results"][str(unique_sensor_id)]["temperature"] == 35.0


# ------------------------
# Empty Result Test
# ------------------------


def test_query_no_matching_data_returns_empty_results(unique_sensor_id):
    """Test querying non-existent sensor returns empty results."""
    response = query_client.get(
        "/query",
        params={
            "sensors": str(unique_sensor_id),  # This sensor has no data
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": "2099-12-31",
            "end_date": "2099-12-31",
        },
    )

    assert response.status_code == 200
    assert response.json()["results"] == {}


def test_query_applies_date_filter_correctly(unique_sensor_id):
    """Ensure metrics outside date range don't affect aggregation."""
    test_date = datetime(2024, 1, 15, 0, 0, 0)

    # Insert data for the target date
    target_payloads = [
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 20,
            "timestamp": test_date.isoformat(),
        },
        {
            "sensor_id": unique_sensor_id,
            "metric_type": "temperature",
            "value": 24,
            "timestamp": (test_date + timedelta(hours=1)).isoformat(),
        },
    ]

    for payload in target_payloads:
        response = ingest_client.post("/metrics", json=payload)
        assert response.status_code == 201

    # Insert OUT-OF-RANGE data (day before)
    out_of_range_payload = {
        "sensor_id": unique_sensor_id,
        "metric_type": "temperature",
        "value": 100,  # would skew avg if included
        "timestamp": (test_date - timedelta(days=1)).isoformat(),
    }

    response = ingest_client.post("/metrics", json=out_of_range_payload)
    assert response.status_code == 201

    # Query ONLY the intended date range
    response = query_client.get(
        "/query",
        params={
            "sensors": str(unique_sensor_id),
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": test_date.strftime("%Y-%m-%d"),
            "end_date": (test_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    )

    assert response.status_code == 200
    body = response.json()

    # Avg should still be (20 + 24) / 2 = 22.0
    assert body["results"][str(unique_sensor_id)]["temperature"] == 22.0


# ------------------------
# Invalid Input Tests
# ------------------------


@pytest.mark.parametrize(
    "params",
    [
        {
            "sensors": "abc",
            "metrics": "temperature",
        },  # invalid sensor ids
        {
            "sensors": "1",
            "metrics": "",
        },  # empty metrics
    ],
)
def test_query_invalid_parameters(params):
    response = query_client.get("/query", params=params)
    assert response.status_code in (400, 422)


def test_query_missing_statistic_with_date_range():
    """Test missing statistic with date range."""
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature",
            "start_date": "2024-01-15",
            "end_date": "2024-01-16",
        },
    )

    assert response.status_code in (400, 422)  # Missing required statistic


def test_query_invalid_statistic_with_date_range():
    """Test invalid statistic value with date range."""
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature",
            "statistic": "median",
            "start_date": "2024-01-15",
            "end_date": "2024-01-16",
        },
    )

    assert response.status_code == 422  # Invalid statistic value
