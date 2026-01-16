import pytest
from fastapi.testclient import TestClient

from ingest.app import app

client = TestClient(app)


# ------------------------
# Valid Inputs
# ------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {
            "sensor_id": 1,
            "metric_type": "temperature",
            "value": 22.5,
        },
        {
            "sensor_id": 10,
            "metric_type": "humidity",
            "value": 55.0,
        },
        {
            "sensor_id": 2,
            "metric_type": "wind_speed",
            "value": 12.3,
        },
        {
            "sensor_id": 3,
            "metric_type": "temperature",
            "value": -5.0,  # valid edge case
        },
    ],
)
def test_ingest_valid_inputs(payload):
    response = client.post("/metrics", json=payload)
    assert response.status_code == 201
    assert "id" in response.json()


# ------------------------
# Invalid Inputs (Schema-Level)
# ------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {},  # empty payload
        {
            "metric_type": "temperature",
            "value": 22.5,
        },  # missing sensor_id
        {
            "sensor_id": -1,
            "metric_type": "temperature",
            "value": 22.5,
        },  # invalid sensor_id
        {
            "sensor_id": 1,
            "metric_type": "pressure",
            "value": 22.5,
        },  # unsupported metric_type
        {
            "sensor_id": 1,
            "metric_type": "temperature",
            "value": "hot",
        },  # invalid value type
    ],
)
def test_ingest_schema_validation_errors(payload):
    response = client.post("/metrics", json=payload)
    assert response.status_code == 422


# ------------------------
# Invalid Inputs (Logic-Level / Edge Cases)
# ------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {
            "sensor_id": 1,
            "metric_type": "",
            "value": 22.5,
        },  # empty metric_type
        {
            "sensor_id": 1,
            "metric_type": "temperature",
            "value": None,
        },  # null value
    ],
)
def test_ingest_logic_level_errors(payload):
    response = client.post("/metrics", json=payload)
    assert response.status_code in (400, 422)
