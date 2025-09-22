import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.geocode import normalize_postcode, geocode_postcode, clear_cache


class TestPostcodeNormalization:
    """Test postcode normalization functionality."""
    
    def test_normalize_spaced_postcode(self):
        """Test normalization of already spaced postcodes."""
        assert normalize_postcode("EC1A 1BB") == "EC1A 1BB"
        assert normalize_postcode("N14 6BS") == "N14 6BS"
        assert normalize_postcode("SW1A 1AA") == "SW1A 1AA"
    
    def test_normalize_unspaced_postcode(self):
        """Test normalization of unspaced postcodes."""
        assert normalize_postcode("EC1A1BB") == "EC1A 1BB"
        assert normalize_postcode("N146BS") == "N14 6BS"
        assert normalize_postcode("SW1A1AA") == "SW1A 1AA"
    
    def test_normalize_mixed_case(self):
        """Test normalization with mixed case."""
        assert normalize_postcode("ec1a1bb") == "EC1A 1BB"
        assert normalize_postcode("n14 6bs") == "N14 6BS"
        assert normalize_postcode("Sw1A 1aA") == "SW1A 1AA"
    
    def test_normalize_extra_spaces(self):
        """Test normalization with extra spaces."""
        assert normalize_postcode("  EC1A   1BB  ") == "EC1A 1BB"
        assert normalize_postcode("N14\t6BS") == "N14 6BS"
        assert normalize_postcode("SW1A\n1AA") == "SW1A 1AA"
    
    def test_normalize_short_postcodes(self):
        """Test normalization of shorter postcodes."""
        assert normalize_postcode("M1 1AA") == "M1 1AA"
        assert normalize_postcode("M11AA") == "M1 1AA"
        assert normalize_postcode("B33 8TH") == "B33 8TH"
    
    def test_normalize_invalid_postcodes(self):
        """Test normalization of invalid inputs."""
        assert normalize_postcode("") == ""
        assert normalize_postcode("   ") == ""
        assert normalize_postcode("123") == "123"  # Too short, returned as-is
        assert normalize_postcode("INVALID") == "INVALID"  # Invalid format


@pytest.mark.asyncio
class TestGeocodePostcode:
    """Test geocoding functionality with mocked HTTP responses."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_success(self, mock_client_class):
        """Test successful geocoding."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "result": {
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await geocode_postcode("EC1A 1BB")
        
        assert result == (51.5074, -0.1278)
        mock_client.get.assert_called_once()
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_not_found(self, mock_client_class):
        """Test geocoding with postcode not found."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await geocode_postcode("INVALID")
        
        assert result is None
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_server_error_with_retry(self, mock_client_class):
        """Test geocoding with server error and retry logic."""
        # First call returns 500, second call succeeds
        mock_response_error = AsyncMock()
        mock_response_error.status_code = 500
        
        mock_response_success = AsyncMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "status": 200,
            "result": {
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.side_effect = [mock_response_error, mock_response_success]
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await geocode_postcode("EC1A 1BB")
        
        assert result == (51.5074, -0.1278)
        assert mock_client.get.call_count == 2
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_timeout_with_retry(self, mock_client_class):
        """Test geocoding with timeout and retry logic."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            httpx.TimeoutException("Timeout"),
            AsyncMock(status_code=200, json=lambda: {
                "status": 200,
                "result": {"latitude": 51.5074, "longitude": -0.1278}
            })
        ]
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await geocode_postcode("EC1A 1BB")
        
        assert result == (51.5074, -0.1278)
        assert mock_client.get.call_count == 2
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_persistent_error(self, mock_client_class):
        """Test geocoding with persistent errors."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("Persistent timeout")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await geocode_postcode("EC1A 1BB")
        
        assert result is None
        assert mock_client.get.call_count == 2  # Original + 1 retry
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_caching(self, mock_client_class):
        """Test that geocoding results are cached."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "result": {
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # First call should hit the API
        result1 = await geocode_postcode("EC1A 1BB")
        assert result1 == (51.5074, -0.1278)
        
        # Second call should use cache
        result2 = await geocode_postcode("EC1A 1BB")
        assert result2 == (51.5074, -0.1278)
        
        # API should only be called once
        mock_client.get.assert_called_once()
    
    @patch('app.services.geocode.httpx.AsyncClient')
    async def test_geocode_invalid_response_format(self, mock_client_class):
        """Test geocoding with invalid response format."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "result": {
                "latitude": None,  # Invalid latitude
                "longitude": -0.1278
            }
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await geocode_postcode("EC1A 1BB")
        
        assert result is None
