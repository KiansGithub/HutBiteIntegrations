import asyncio
import logging
import re
from typing import Optional, Tuple
import httpx
from cachetools import TTLCache
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory cache for geocoded postcodes
_postcode_cache = TTLCache(maxsize=1000, ttl=settings.POSTCODE_TTL_SECONDS)


def normalize_postcode(postcode: str) -> str:
    """
    Normalize UK postcode by trimming, uppercasing, and collapsing spaces.
    Accepts both spaced (EC1A 1BB) and unspaced (EC1A1BB) formats.
    """
    if not postcode:
        return ""
    
    # Remove all whitespace and convert to uppercase
    normalized = re.sub(r'\s+', '', postcode.strip().upper())
    
    # UK postcodes have format: 1-2 letters + 1-2 digits + optional letter + space + 1 digit + 2 letters
    # Insert space before the last 3 characters for proper UK postcode format
    if len(normalized) >= 5:
        return f"{normalized[:-3]} {normalized[-3:]}"
    
    return normalized


async def geocode_postcode(postcode: str) -> Optional[Tuple[float, float]]:
    """
    Geocode a UK postcode using postcodes.io API.
    Returns (latitude, longitude) tuple or None if not found/error.
    Implements caching and retry logic with jittered backoff.
    """
    normalized = normalize_postcode(postcode)
    
    if not normalized:
        logger.warning(f"Invalid postcode format: {postcode}")
        return None
    
    # Check cache first
    if normalized in _postcode_cache:
        logger.info(f"Cache hit for postcode: {normalized}")
        return _postcode_cache[normalized]
    
    # Make API request with retry logic
    url = f"{settings.POSTCODES_BASE_URL}/postcodes/{normalized}"
    
    async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
        for attempt in range(2):  # Original + 1 retry
            try:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == 200 and "result" in data:
                        result = data["result"]
                        lat = result.get("latitude")
                        lon = result.get("longitude")
                        
                        if lat is not None and lon is not None:
                            coords = (float(lat), float(lon))
                            _postcode_cache[normalized] = coords
                            logger.info(f"Successfully geocoded {normalized}: {coords}")
                            return coords
                
                elif response.status_code == 404:
                    # Postcode not found - don't retry
                    logger.warning(f"Postcode not found: {normalized}")
                    return None
                
                elif response.status_code >= 500 and attempt == 0:
                    # Server error - retry once with jittered backoff
                    jitter = 0.1 + (0.2 * (attempt + 1))  # 0.1-0.3s jitter
                    await asyncio.sleep(jitter)
                    logger.warning(f"Server error {response.status_code} for {normalized}, retrying...")
                    continue
                
                else:
                    logger.error(f"API error {response.status_code} for {normalized}")
                    return None
                    
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt == 0:
                    # Network error - retry once with jittered backoff
                    jitter = 0.1 + (0.2 * (attempt + 1))
                    await asyncio.sleep(jitter)
                    logger.warning(f"Network error for {normalized}, retrying: {e}")
                    continue
                else:
                    logger.error(f"Network error for {normalized} after retry: {e}")
                    return None
            
            except Exception as e:
                logger.error(f"Unexpected error geocoding {normalized}: {e}")
                return None
    
    return None


def clear_cache():
    """Clear the postcode cache - useful for testing."""
    _postcode_cache.clear()
