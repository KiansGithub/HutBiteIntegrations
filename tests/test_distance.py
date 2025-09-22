import pytest
import math
from app.services.distance import haversine_distance, calculate_delivery_distance


class TestHaversineDistance:
    """Test the Haversine distance calculation with known coordinate pairs."""
    
    def test_haversine_same_point(self):
        """Test distance between same point should be 0."""
        distance = haversine_distance(51.5074, -0.1278, 51.5074, -0.1278)
        assert distance == 0.0
    
    def test_haversine_known_distance(self):
        """Test with known distance between London and Manchester."""
        # London coordinates
        london_lat, london_lon = 51.5074, -0.1278
        # Manchester coordinates  
        manchester_lat, manchester_lon = 53.4808, -2.2426
        
        # Known distance is approximately 163 miles
        distance = haversine_distance(london_lat, london_lon, manchester_lat, manchester_lon)
        
        # Allow 1 mile tolerance for calculation differences
        assert abs(distance - 163.0) < 1.0
    
    def test_haversine_short_distance(self):
        """Test with short distance within London."""
        # London Bridge
        lat1, lon1 = 51.5081, -0.0759
        # Tower Bridge (approximately 0.5 miles away)
        lat2, lon2 = 51.5055, -0.0754
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 0.2 miles
        assert 0.1 < distance < 0.4
    
    def test_haversine_cross_hemisphere(self):
        """Test distance calculation across hemispheres."""
        # London
        lat1, lon1 = 51.5074, -0.1278
        # Sydney
        lat2, lon2 = -33.8688, 151.2093
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Distance should be approximately 10,500 miles
        assert 10400 < distance < 10600
    
    def test_calculate_delivery_distance(self):
        """Test the wrapper function for delivery distance calculation."""
        restaurant_coords = (51.5074, -0.1278)  # London
        customer_coords = (51.5081, -0.0759)    # London Bridge
        
        distance = calculate_delivery_distance(restaurant_coords, customer_coords)
        
        # Should be a short distance within London
        assert 0.1 < distance < 5.0
    
    def test_haversine_precision(self):
        """Test precision of Haversine calculation."""
        # Very close points (about 100 meters apart)
        lat1, lon1 = 51.5074, -0.1278
        lat2, lon2 = 51.5083, -0.1278  # Slightly north
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 0.06 miles (100 meters)
        assert 0.05 < distance < 0.08
    
    def test_haversine_edge_cases(self):
        """Test edge cases for coordinate values."""
        # North Pole to South Pole
        distance_poles = haversine_distance(90, 0, -90, 0)
        
        # Should be approximately half the Earth's circumference
        expected_half_circumference = math.pi * 3959  # Earth radius in miles
        assert abs(distance_poles - expected_half_circumference) < 10
        
        # Equator opposite sides
        distance_equator = haversine_distance(0, 0, 0, 180)
        assert abs(distance_equator - expected_half_circumference) < 10
