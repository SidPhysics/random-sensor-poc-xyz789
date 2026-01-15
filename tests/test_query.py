import pytest
from fastapi.testclient import TestClient

from ingest.app import app as ingest_app
from query.app import app as query_app

from shared.database import get_db
from shared.models import Metric



ingest_client = TestClient(ingest_app)
query_client = TestClient(query_app)


# ------------------------
# Test Setup: Seed Data
# ------------------------

@pytest.fixture(scope="module", autouse=True)
def seed_data():
    # clear existing data
    db = next(get_db())
    try:

        db.query(Metric).delete()
        db.commit()

        payloads = [
            {"sensor_id": 1, "metric_type": "temperature", "value": 20},
            {"sensor_id": 1, "metric_type": "temperature", "value": 24},
            {"sensor_id": 1, "metric_type": "humidity", "value": 50},
            {"sensor_id": 2, "metric_type": "temperature", "value": 30},
        ]

        for payload in payloads:
            response = ingest_client.post("/metrics", json=payload)
            assert response.status_code == 201

    finally:
        db.close()
# ------------------------
# Valid Query Tests
# ------------------------

def test_query_avg_temperature_single_sensor():
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature",
            "statistic": "avg",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["statistic"] == "avg"
    assert body["results"]["1"]["temperature"] == 22.0


def test_query_multiple_metrics():
    response = query_client.get(
        "/query",
        params={
            "sensors": "1",
            "metrics": "temperature,humidity",
            "statistic": "avg",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["results"]["1"]["temperature"] == 22.0
    assert body["results"]["1"]["humidity"] == 50.0


def test_query_all_sensors_max_temperature():
    response = query_client.get(
        "/query",
        params={
            "sensors": "all",
            "metrics": "temperature",
            "statistic": "max",
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
    response = query_client.get(
        "/query",
        params={
            "sensors": "999",
            "metrics": "temperature",
            "statistic": "avg",
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
