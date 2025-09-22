import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.geocode import clear_cache

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_geocode_cache():
    """Clear geocode cache before each test."""
    clear_cache()


class TestDeliverabilityAPI:
    """Integration tests for the deliverability check endpoint."""
    
    @patch('app.services.geocode.httpx.AsyncClient')
    def test_deliverability_check_success_within_range(self, mock_client_class):
        """Test successful deliverability check within delivery range."""
        # Mock successful geocoding response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "result": {
                "latitude": 51.5081,  # Close to restaurant
                "longitude": -0.0759
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Request payload
        payload = {
            "restaurant": {"lat": 51.5074, "lon": -0.1278},
            "customer_postcode": "EC1A 1BB",
            "radius_miles": 3.0
        }
        
        response = client.post("/deliverability/check", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["deliverable"] is True
        assert data["normalized_postcode"] == "EC1A 1BB"
        assert data["reason"] == "OK"
        assert data["source"] == "api"
        assert isinstance(data["distance_miles"], float)
        assert data["distance_miles"] < 3.0
    
    @patch('app.services.geocode.httpx.AsyncClient')
    def test_deliverability_check_out_of_range(self, mock_client_class):
        """Test deliverability check for location outside delivery range."""
        # Mock geocoding response for distant location
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "result": {
                "latitude": 53.4808,  # Manchester - far from London restaurant
                "longitude": -2.2426
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        payload = {
            "restaurant": {"lat": 51.5074, "lon": -0.1278},  # London
            "customer_postcode": "M1 1AA",  # Manchester
            "radius_miles": 3.0
        }
        
        response = client.post("/deliverability/check", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["deliverable"] is False
        assert data["normalized_postcode"] == "M1 1AA"
        assert data["reason"] == "OUT_OF_RANGE"
        assert data["source"] == "api"
        assert data["distance_miles"] > 3.0
    
    @patch('app.services.geocode.httpx.AsyncClient')
    def test_deliverability_check_invalid_postcode(self, mock_client_class):
        """Test deliverability check with invalid postcode."""
        # Mock 404 response for invalid postcode
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        payload = {
            "restaurant": {"lat": 51.5074, "lon": -0.1278},
            "customer_postcode": "INVALID123",
            "radius_miles": 3.0
        }
        
        response = client.post("/deliverability/check", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["deliverable"] is False
        assert data["normalized_postcode"] == "INVALID 123"
        assert data["reason"] == "INVALID_POSTCODE"
        assert data["source"] == "api"
        assert data["distance_miles"] is None
    
    def test_deliverability_check_unspaced_postcode(self):
        """Test deliverability check with unspaced postcode format."""
        with patch('app.services.geocode.httpx.AsyncClient') as mock_client_class:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": 200,
                "result": {
                    "latitude": 51.5081,
                    "longitude": -0.0759
                }
            }
            
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            payload = {
                "restaurant": {"lat": 51.5074, "lon": -0.1278},
                "customer_postcode": "EC1A1BB",  # Unspaced format
                "radius_miles": 3.0
            }
            
            response = client.post("/deliverability/check", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["normalized_postcode"] == "EC1A 1BB"  # Should be normalized
    
    def test_deliverability_check_default_radius(self):
        """Test deliverability check with default radius when not specified."""
        with patch('app.services.geocode.httpx.AsyncClient') as mock_client_class:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": 200,
                "result": {
                    "latitude": 51.5081,
                    "longitude": -0.0759
                }
            }
            
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            payload = {
                "restaurant": {"lat": 51.5074, "lon": -0.1278},
                "customer_postcode": "EC1A 1BB"
                # No radius_miles specified - should use default 3.0
            }
            
            response = client.post("/deliverability/check", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["deliverable"] is True  # Should be within default 3 mile radius
    
    def test_deliverability_check_invalid_restaurant_coordinates(self):
        """Test deliverability check with invalid restaurant coordinates."""
        payload = {
            "restaurant": {"lat": 91.0, "lon": -0.1278},  # Invalid latitude > 90
            "customer_postcode": "EC1A 1BB",
            "radius_miles": 3.0
        }
        
        response = client.post("/deliverability/check", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_deliverability_check_missing_required_fields(self):
        """Test deliverability check with missing required fields."""
        payload = {
            "restaurant": {"lat": 51.5074, "lon": -0.1278}
            # Missing customer_postcode
        }
        
        response = client.post("/deliverability/check", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.geocode.httpx.AsyncClient')
    def test_deliverability_check_geocode_error(self, mock_client_class):
        """Test deliverability check when geocoding service fails."""
        # Mock network timeout
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Network error")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        payload = {
            "restaurant": {"lat": 51.5074, "lon": -0.1278},
            "customer_postcode": "EC1A 1BB",
            "radius_miles": 3.0
        }
        
        response = client.post("/deliverability/check", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["deliverable"] is False
        assert data["reason"] == "GEOCODE_ERROR"
        assert data["distance_miles"] is None
    
    @patch('app.services.geocode.httpx.AsyncClient')
    def test_deliverability_check_caching(self, mock_client_class):
        """Test that subsequent requests use cached geocoding results."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "result": {
                "latitude": 51.5081,
                "longitude": -0.0759
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        payload = {
            "restaurant": {"lat": 51.5074, "lon": -0.1278},
            "customer_postcode": "EC1A 1BB",
            "radius_miles": 3.0
        }
        
        # First request
        response1 = client.post("/deliverability/check", json=payload)
        assert response1.status_code == 200
        assert response1.json()["source"] == "api"
        
        # Second request should use cache
        response2 = client.post("/deliverability/check", json=payload)
        assert response2.status_code == 200
        assert response2.json()["source"] == "cache"
        
        # API should only be called once
        mock_client.get.assert_called_once()
    
    def test_deliverability_check_edge_radius_values(self):
        """Test deliverability check with edge radius values."""
        with patch('app.services.geocode.httpx.AsyncClient') as mock_client_class:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": 200,
                "result": {
                    "latitude": 51.5081,
                    "longitude": -0.0759
                }
            }
            
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Test minimum radius
            payload = {
                "restaurant": {"lat": 51.5074, "lon": -0.1278},
                "customer_postcode": "EC1A 1BB",
                "radius_miles": 0.1
            }
            
            response = client.post("/deliverability/check", json=payload)
            assert response.status_code == 200
            
            # Test maximum radius
            payload["radius_miles"] = 50.0
            response = client.post("/deliverability/check", json=payload)
            assert response.status_code == 200
            
            # Test invalid radius (too small)
            payload["radius_miles"] = 0.05
            response = client.post("/deliverability/check", json=payload)
            assert response.status_code == 422
