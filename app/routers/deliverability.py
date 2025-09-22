import logging
import uuid
from fastapi import APIRouter, HTTPException
from app.schemas.deliverability import (
    DeliverabilityCheckRequest, 
    DeliverabilityCheckResponse,
    DeliverabilityErrorResponse
)
from app.services.geocode import geocode_postcode, normalize_postcode, _postcode_cache
from app.services.distance import calculate_delivery_distance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deliverability", tags=["deliverability"])


@router.post(
    "/check",
    response_model=DeliverabilityCheckResponse,
    summary="Check delivery availability",
    description="Check if delivery is possible to a UK postcode from a restaurant location"
)
async def check_deliverability(request: DeliverabilityCheckRequest) -> DeliverabilityCheckResponse:
    """
    Check if delivery is possible from restaurant to customer postcode.
    
    Core logic:
    1. Normalize postcode
    2. Geocode postcode → {lat, lon} using postcodes.io
    3. Compute distance from restaurant to customer with Haversine
    4. Decision: deliverable = distance_miles <= radius_miles + buffer_miles
    """
    # Generate request ID for logging
    request_id = str(uuid.uuid4())[:8]
    
    # Validate restaurant coordinates
    restaurant_lat = request.restaurant.lat
    restaurant_lon = request.restaurant.lon
    
    if not (-90 <= restaurant_lat <= 90) or not (-180 <= restaurant_lon <= 180):
        logger.error(f"[{request_id}] Invalid restaurant coordinates: {restaurant_lat}, {restaurant_lon}")
        raise HTTPException(
            status_code=500, 
            detail="Invalid restaurant coordinates"
        )
    
    # Normalize postcode
    normalized_postcode = normalize_postcode(request.customer_postcode)
    
    if not normalized_postcode:
        logger.warning(f"[{request_id}] Invalid postcode format: {request.customer_postcode}")
        return DeliverabilityCheckResponse(
            deliverable=False,
            distance_miles=None,
            normalized_postcode=request.customer_postcode,
            reason="INVALID_POSTCODE",
            source="api"
        )
    
    # Check if coordinates are cached
    source = "cache" if normalized_postcode in _postcode_cache else "api"
    
    # Geocode customer postcode
    customer_coords = await geocode_postcode(request.customer_postcode)
    
    if customer_coords is None:
        logger.warning(f"[{request_id}] Failed to geocode postcode: {normalized_postcode}")
        return DeliverabilityCheckResponse(
            deliverable=False,
            distance_miles=None,
            normalized_postcode=normalized_postcode,
            reason="INVALID_POSTCODE" if normalized_postcode else "GEOCODE_ERROR",
            source=source
        )
    
    # Calculate distance
    restaurant_coords = (restaurant_lat, restaurant_lon)
    distance_miles = calculate_delivery_distance(restaurant_coords, customer_coords)
    
    # Apply delivery decision logic with buffer
    radius_miles = request.radius_miles or 3.0
    buffer_miles = 0.05  # Small buffer to avoid edge rejections
    deliverable = distance_miles <= (radius_miles + buffer_miles)
    
    reason = "OK" if deliverable else "OUT_OF_RANGE"
    
    # Log the decision
    logger.info(
        f"[{request_id}] Deliverability check: "
        f"postcode={normalized_postcode}, "
        f"distance={distance_miles:.2f}mi, "
        f"radius={radius_miles}mi, "
        f"deliverable={deliverable}, "
        f"reason={reason}, "
        f"source={source}"
    )
    
    return DeliverabilityCheckResponse(
        deliverable=deliverable,
        distance_miles=round(distance_miles, 2),
        normalized_postcode=normalized_postcode,
        reason=reason,
        source=source
    )
