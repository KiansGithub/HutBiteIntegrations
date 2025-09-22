import math
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in decimal degrees
        lat2, lon2: Latitude and longitude of second point in decimal degrees
    
    Returns:
        Distance in miles
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in miles
    earth_radius_miles = 3959.0
    
    # Calculate the distance
    distance = earth_radius_miles * c
    
    return distance


def calculate_delivery_distance(
    restaurant_coords: Tuple[float, float], 
    customer_coords: Tuple[float, float]
) -> float:
    """
    Calculate delivery distance between restaurant and customer coordinates.
    
    Args:
        restaurant_coords: (latitude, longitude) of restaurant
        customer_coords: (latitude, longitude) of customer
    
    Returns:
        Distance in miles
    """
    restaurant_lat, restaurant_lon = restaurant_coords
    customer_lat, customer_lon = customer_coords
    
    return haversine_distance(restaurant_lat, restaurant_lon, customer_lat, customer_lon)
