"""
Integration tests for deployed Weather Sensor API.
Tests the live API Gateway + Lambda + RDS stack.
"""
import requests
import pytest
import os


@pytest.fixture
def api_base_url():
    """Get API base URL from environment or use default."""
    return os.getenv("API_BASE_URL", "https://dsiuqwaqe3.execute-api.us-east-1.amazonaws.com/prod")


class TestIngestIntegration:
    """Test the ingest endpoint against live API."""
    
    def test_ingest_valid_metric_success(self, api_base_url):
        """Test successful metric ingestion."""
        payload = {
            "sensor_id": 999,
            "metric_type": "temperature",
            "value": 25.5,
            "timestamp": "2099-01-01T10:00:00"
        }
        
        response = requests.post(f"{api_base_url}/metrics", json=payload, timeout=30)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Metric ingested successfully"
        assert "id" in data
    
    def test_ingest_invalid_payload_returns_422(self, api_base_url):
        """Test validation error handling."""
        payload = {
            "sensor_id": "invalid",  # Should be int
            "metric_type": "temperature",
            "value": 25.5
            # Missing timestamp
        }
        
        response = requests.post(f"{api_base_url}/metrics", json=payload, timeout=30)
        
        assert response.status_code == 422
        assert "detail" in response.json()


class TestQueryIntegration:
    """Test the query endpoint against live API."""
    
    def test_query_existing_data_success(self, api_base_url):
        """Test querying existing data."""
        params = {
            "sensors": "1",
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": "2024-01-15",
            "end_date": "2024-01-16"
        }
        
        response = requests.get(f"{api_base_url}/query", params=params, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        assert data["statistic"] == "avg"
        assert "results" in data
    
    def test_query_invalid_statistic_returns_422(self, api_base_url):
        """Test invalid statistic parameter."""
        params = {
            "sensors": "1",
            "metrics": "temperature",
            "statistic": "invalid",
            "start_date": "2024-01-15",
            "end_date": "2024-01-16"
        }
        
        response = requests.get(f"{api_base_url}/query", params=params, timeout=30)
        
        assert response.status_code == 422


class TestEndToEndFlow:
    """Test complete ingest → query flow."""
    
    def test_ingest_then_query_flow(self, api_base_url):
        """Test ingesting data then querying it back."""
        # Step 1: Ingest test data
        test_data = [
            {
                "sensor_id": 888,
                "metric_type": "temperature", 
                "value": 20.0,
                "timestamp": "2099-06-01T10:00:00"
            },
            {
                "sensor_id": 888,
                "metric_type": "temperature",
                "value": 30.0, 
                "timestamp": "2099-06-01T11:00:00"
            }
        ]
        
        for payload in test_data:
            response = requests.post(f"{api_base_url}/metrics", json=payload, timeout=30)
            assert response.status_code == 201
        
        # Step 2: Query the data back
        params = {
            "sensors": "888",
            "metrics": "temperature",
            "statistic": "avg",
            "start_date": "2099-06-01",
            "end_date": "2099-06-02"
        }
        
        response = requests.get(f"{api_base_url}/query", params=params, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        assert "888" in data["results"]
        assert data["results"]["888"]["temperature"] == 25.0  # Average of 20.0 and 30.0