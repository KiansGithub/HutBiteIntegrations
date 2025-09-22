# HutBite Integrations

A FastAPI-based service for HubRise integrations and UK postcode deliverability checking.

## Features

### Deliverability Checking
- **UK Postcode Geocoding**: Uses postcodes.io API to convert UK postcodes to coordinates
- **Distance Calculation**: Haversine formula for accurate distance calculations
- **Intelligent Caching**: TTL-based caching to reduce API calls and improve performance
- **Retry Logic**: Automatic retry with jittered backoff for network resilience
- **Postcode Normalization**: Handles both spaced ("EC1A 1BB") and unspaced ("EC1A1BB") formats

### HubRise Integration
- OAuth2 authentication flow
- Orders management
- Catalog synchronization
- Session-based authentication

## Quick Start

### Prerequisites
- Python 3.8+
- pip or poetry

### Installation

#### Using pip
```bash
# Clone the repository
git clone https://github.com/hutbite/integrations.git
cd integrations

# Install dependencies
pip install -r app/requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

#### Using poetry (recommended)
```bash
# Clone the repository
git clone https://github.com/hutbite/integrations.git
cd integrations

# Install dependencies
poetry install

# Install with development dependencies
poetry install --with dev
```

### Environment Configuration

Create a `.env` file in the `app/` directory:

```env
# HubRise Configuration
HUBRISE_CLIENT_ID=your_hubrise_client_id
HUBRISE_CLIENT_SECRET=your_hubrise_client_secret

# Optional: Postcodes.io Configuration
POSTCODES_BASE_URL=https://api.postcodes.io
POSTCODE_TTL_SECONDS=86400
HTTP_TIMEOUT_SECONDS=6

# Application Configuration
SESSION_SECRET=your_session_secret_key
APP_BASE_URL=http://localhost:8000
```

### Running the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000` with automatic OpenAPI documentation at `http://localhost:8000/docs`.

## API Documentation

### Deliverability Check

Check if delivery is possible from a restaurant to a UK postcode.

**Endpoint:** `POST /deliverability/check`

**Request Body:**
```json
{
  "restaurant": {
    "lat": 51.5074,
    "lon": -0.1278
  },
  "customer_postcode": "N14 6BS",
  "radius_miles": 3.0
}
```

**Response (Success):**
```json
{
  "deliverable": true,
  "distance_miles": 2.34,
  "normalized_postcode": "N14 6BS",
  "reason": "OK",
  "source": "api"
}
```

**Response (Out of Range):**
```json
{
  "deliverable": false,
  "distance_miles": 5.67,
  "normalized_postcode": "M1 1AA",
  "reason": "OUT_OF_RANGE",
  "source": "cache"
}
```

**Response (Invalid Postcode):**
```json
{
  "deliverable": false,
  "distance_miles": null,
  "normalized_postcode": "INVALID123",
  "reason": "INVALID_POSTCODE",
  "source": "api"
}
```

#### Parameters

- `restaurant.lat` (required): Restaurant latitude (-90 to 90)
- `restaurant.lon` (required): Restaurant longitude (-180 to 180)
- `customer_postcode` (required): UK postcode (spaced or unspaced format)
- `radius_miles` (optional): Delivery radius in miles (default: 3.0, range: 0.1-50.0)

#### Response Fields

- `deliverable`: Whether delivery is possible
- `distance_miles`: Calculated distance in miles (null if geocoding failed)
- `normalized_postcode`: Standardized postcode format
- `reason`: Decision reason (`OK`, `OUT_OF_RANGE`, `INVALID_POSTCODE`, `GEOCODE_ERROR`)
- `source`: Data source (`api` for fresh data, `cache` for cached data)

### Example Usage

#### cURL
```bash
curl -X POST http://localhost:8000/deliverability/check \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant": {"lat": 51.5074, "lon": -0.1278},
    "customer_postcode": "N14 6BS",
    "radius_miles": 3.0
  }'
```

#### Python
```python
import httpx

async def check_deliverability():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/deliverability/check",
            json={
                "restaurant": {"lat": 51.5074, "lon": -0.1278},
                "customer_postcode": "EC1A1BB",
                "radius_miles": 5.0
            }
        )
        return response.json()

# Result: {"deliverable": true, "distance_miles": 2.1, ...}
```

#### JavaScript
```javascript
const response = await fetch('http://localhost:8000/deliverability/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    restaurant: { lat: 51.5074, lon: -0.1278 },
    customer_postcode: 'SW1A 1AA',
    radius_miles: 2.5
  })
});

const result = await response.json();
console.log(result);
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Project Structure

```
├── app/
│   ├── core/           # Core configuration and utilities
│   ├── models/         # Database models
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic services
│   │   ├── geocode.py  # Postcode geocoding service
│   │   └── distance.py # Distance calculation service
│   └── main.py         # FastAPI application
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTCODES_BASE_URL` | `https://api.postcodes.io` | Postcodes.io API base URL |
| `POSTCODE_TTL_SECONDS` | `86400` | Cache TTL for geocoded postcodes (24 hours) |
| `HTTP_TIMEOUT_SECONDS` | `6` | HTTP request timeout |
| `HUBRISE_CLIENT_ID` | - | HubRise OAuth client ID (required) |
| `HUBRISE_CLIENT_SECRET` | - | HubRise OAuth client secret (required) |
| `SESSION_SECRET` | `dev_change_me` | Session encryption key |
| `APP_BASE_URL` | `http://localhost:8000` | Application base URL |

### Performance Tuning

#### Caching
- Postcode geocoding results are cached for 24 hours by default
- Cache size is limited to 1000 entries (LRU eviction)
- Adjust `POSTCODE_TTL_SECONDS` for different cache durations

#### Timeouts
- Default HTTP timeout is 6 seconds
- Automatic retry on 5xx errors and timeouts
- Jittered backoff to prevent thundering herd

#### Rate Limiting
- Currently not implemented (TODO)
- Consider adding rate limiting for production deployments

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful deliverability check (even if not deliverable)
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Server-side errors (invalid restaurant coordinates, etc.)

### Error Reasons

- `OK`: Delivery is possible
- `OUT_OF_RANGE`: Distance exceeds delivery radius
- `INVALID_POSTCODE`: Postcode not found or invalid format
- `GEOCODE_ERROR`: Network error or API failure

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

COPY app/ ./app/
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Checks

The application provides health check endpoints:
- `GET /health` - Basic health check
- `GET /docs` - OpenAPI documentation

### Monitoring

Consider adding:
- Structured logging with request IDs
- Metrics collection (Prometheus)
- Distributed tracing (Jaeger)
- Error tracking (Sentry)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the development team.
