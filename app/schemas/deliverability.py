from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


class RestaurantLocation(BaseModel):
    """Restaurant location coordinates."""
    lat: float = Field(..., description="Latitude in decimal degrees")
    lon: float = Field(..., description="Longitude in decimal degrees")
    
    @validator('lat')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @validator('lon')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


class DeliverabilityCheckRequest(BaseModel):
    """Request schema for deliverability check."""
    restaurant: RestaurantLocation = Field(..., description="Restaurant location coordinates")
    customer_postcode: str = Field(..., description="Customer UK postcode (e.g., 'N14 6BS' or 'EC1A1BB')")
    radius_miles: Optional[float] = Field(3.0, description="Delivery radius in miles", ge=0.1, le=50.0)


class DeliverabilityCheckResponse(BaseModel):
    """Response schema for deliverability check."""
    deliverable: bool = Field(..., description="Whether delivery is possible")
    distance_miles: Optional[float] = Field(None, description="Calculated distance in miles")
    normalized_postcode: str = Field(..., description="Normalized postcode format")
    reason: Literal["OK", "INVALID_POSTCODE", "GEOCODE_ERROR", "OUT_OF_RANGE"] = Field(
        ..., description="Reason for the deliverability decision"
    )
    source: Literal["api", "cache"] = Field(..., description="Source of geocoding data")


class DeliverabilityErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
