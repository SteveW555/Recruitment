# Location Service

UK Postcode and Geography microservice for ProActive People recruitment platform.

## Overview

The Location Service provides REST API endpoints for:
- **Single & Batch Postcode Lookups**: Get geographic coordinates, town, and county data
- **Postcode Search**: Wildcard search across UK postcodes
- **CSV Processing**: Upload CSV files and automatically extract postcodes
- **Demographics Data**: Access UK socioeconomic data by postcode sector

## Features

- ✅ Full UK postcode database with coordinates
- ✅ Batch processing for high-volume queries
- ✅ Flexible postcode extraction (handles missing spaces)
- ✅ CSV file processing with automatic postcode detection
- ✅ Demographics data for market analysis
- ✅ Fast lookups with indexed database queries
- ✅ Comprehensive error handling and logging

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Processing**: Pandas, NumPy
- **Server**: Uvicorn (ASGI)

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip or uv package manager

### Setup

1. **Install dependencies**:
   ```bash
   cd backend/services/location-service
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   # Copy from project root .env or create service-specific .env
   cp ../../../.env.example .env
   ```

3. **Initialize database**:
   ```bash
   # Ensure PostgreSQL is running and credentials in .env are correct
   # Tables will be created automatically on first run
   ```

4. **Run the service**:
   ```bash
   python -m src.main
   # OR with hot reload for development:
   uvicorn src.main:app --reload --port 8001
   ```

## Configuration

Environment variables (from project root `.env`):

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=recruitment
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_password

# Service
LOCATION_SERVICE_PORT=8001
LOCATION_SERVICE_HOST=0.0.0.0
NODE_ENV=development

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## API Endpoints

### Single Postcode Lookup
```http
GET /api/postcodes/{postcode}
```

**Example:**
```bash
curl http://localhost:8001/api/postcodes/BS1%204DJ
```

**Response:**
```json
{
  "postcode": "BS1 4DJ",
  "lat": 51.4521,
  "lng": -2.5917,
  "town": "Bristol",
  "county": "Bristol"
}
```

### Batch Postcode Lookup
```http
POST /api/postcodes/batch
Content-Type: application/json

{
  "postcodes": ["BS1 4DJ", "BS2 0JA", "BS3 1HL"]
}
```

**Response:**
```json
{
  "BS1 4DJ": {
    "postcode": "BS1 4DJ",
    "lat": 51.4521,
    "lng": -2.5917,
    "town": "Bristol",
    "county": "Bristol"
  },
  "BS2 0JA": { ... },
  "BS3 1HL": { ... }
}
```

### Postcode Search
```http
GET /api/postcodes/search/{pattern}?limit=100
```

**Example:**
```bash
curl http://localhost:8001/api/postcodes/search/BS1?limit=50
```

### CSV Upload with Postcode Extraction
```http
POST /api/postcodes/upload/csv?records=100
Content-Type: multipart/form-data
```

**Example:**
```bash
curl -X POST \
  http://localhost:8001/api/postcodes/upload/csv?records=500 \
  -F "file=@candidates.csv"
```

**Response:**
```json
{
  "column_names": ["postcode", "name", "address", "city", ...],
  "data": [
    {
      "postcode": "BS1 4DJ",
      "name": "John Smith",
      "address": "123 Main St",
      ...
    }
  ],
  "records_returned": 500,
  "total_records": 1250
}
```

### Health Check
```http
GET /health
GET /api/postcodes/health
```

## Database Schema

### `postcodes` Table

| Column   | Type         | Description                      |
|----------|--------------|----------------------------------|
| id       | INTEGER      | Primary key (auto-increment)     |
| postcode | VARCHAR(10)  | UK postcode (unique, indexed)    |
| lat      | FLOAT        | Latitude (WGS84)                 |
| lng      | FLOAT        | Longitude (WGS84)                |
| town     | VARCHAR(100) | Town/city name (indexed)         |
| county   | VARCHAR(100) | County name (indexed)            |

**Indexes:**
- `postcodes_pkey` (PRIMARY KEY on id)
- `ix_postcodes_postcode` (UNIQUE on postcode)
- `idx_postcode_town` (on town)
- `idx_postcode_county` (on county)
- `idx_postcode_coordinates` (on lat, lng)

### `demographics` Table

| Column            | Type         | Description                         |
|-------------------|--------------|-------------------------------------|
| id                | INTEGER      | Primary key                         |
| postcode_sector   | VARCHAR(10)  | Postcode sector (e.g., "BS1 4")     |
| population        | INTEGER      | Total population                    |
| social_grade_ab   | FLOAT        | % AB (Higher managerial)            |
| social_grade_c1   | FLOAT        | % C1 (Supervisory)                  |
| social_grade_c2   | FLOAT        | % C2 (Skilled manual)               |
| social_grade_de   | FLOAT        | % DE (Semi/unskilled)               |
| median_income     | FLOAT        | Median household income (GBP)       |
| employment_rate   | FLOAT        | Employment rate (%)                 |
| data_source       | VARCHAR(100) | Source of demographic data          |

## Postcode Format

UK postcodes follow the format: `XX## #XX`

**Components:**
- **Area**: 1-2 letters (e.g., "BS")
- **District**: Area + 1-2 digits (e.g., "BS1")
- **Sector**: District + 1 digit (e.g., "BS1 4")
- **Unit**: Sector + 2 letters (e.g., "BS1 4DJ")

**Utility Functions** (`src/utils/postcode_utils.py`):
- `extract_uk_postcode_from_string()`: Extract from address (requires space)
- `extract_uk_postcode_from_string_flexible()`: Extract from address (handles missing space)
- `extract_postcode_sector()`: Get sector from full postcode
- `extract_postcode_district()`: Get district from full postcode
- `extract_postcode_area()`: Get area from full postcode
- `normalize_postcode()`: Standardize postcode format
- `validate_uk_postcode()`: Check if valid UK postcode

## Performance

- **Single Lookup**: <10ms (indexed query)
- **Batch Lookup (100 postcodes)**: <50ms
- **CSV Processing (1000 rows)**: <500ms
- **Search (pattern matching)**: <100ms (with limit)

## Integration Examples

### Python (requests)
```python
import requests

# Single lookup
response = requests.get("http://localhost:8001/api/postcodes/BS1 4DJ")
data = response.json()
print(f"{data['postcode']}: {data['lat']}, {data['lng']}")

# Batch lookup
batch_response = requests.post(
    "http://localhost:8001/api/postcodes/batch",
    json={"postcodes": ["BS1 4DJ", "BS2 0JA"]}
)
batch_data = batch_response.json()
```

### JavaScript (fetch)
```javascript
// Single lookup
const response = await fetch('http://localhost:8001/api/postcodes/BS1 4DJ');
const data = await response.json();
console.log(`${data.postcode}: ${data.lat}, ${data.lng}`);

// Batch lookup
const batchResponse = await fetch('http://localhost:8001/api/postcodes/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ postcodes: ['BS1 4DJ', 'BS2 0JA'] })
});
const batchData = await batchResponse.json();
```

### cURL
```bash
# Single lookup
curl http://localhost:8001/api/postcodes/BS1%204DJ

# Batch lookup
curl -X POST http://localhost:8001/api/postcodes/batch \
  -H "Content-Type: application/json" \
  -d '{"postcodes": ["BS1 4DJ", "BS2 0JA"]}'

# CSV upload
curl -X POST http://localhost:8001/api/postcodes/upload/csv?records=100 \
  -F "file=@data.csv"
```

## Testing

```bash
# Run unit tests
pytest tests/

# Test single endpoint
curl http://localhost:8001/api/postcodes/BS1%204DJ

# Test health check
curl http://localhost:8001/health
```

## API Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Error Handling

The service returns standard HTTP status codes:

- `200 OK`: Successful request
- `404 Not Found`: Postcode not found in database
- `422 Unprocessable Entity`: Invalid request format
- `500 Internal Server Error`: Server-side error

All errors include a `detail` field with explanation:
```json
{
  "detail": "Postcode 'INVALID' not found"
}
```

## Logging

Logs include:
- Request/response details
- Database query performance
- Error stack traces
- Service lifecycle events

Log format:
```
2025-01-15 10:30:45 - location-service - INFO - Looking up postcode: BS1 4DJ
2025-01-15 10:30:45 - location-service - INFO - Postcode found: BS1 4DJ
```

## Security

- ✅ Input validation on all endpoints
- ✅ SQL injection protection (parameterized queries)
- ✅ CORS configuration for cross-origin requests
- ✅ Rate limiting (configure at API Gateway)
- ✅ Request size limits (10MB for CSV uploads)

## Integration with Other Services

This service integrates with:
- **Candidate Service**: Postcode-based candidate location
- **Client Service**: Client company location data
- **Matching Service**: Geographic matching radius
- **Analytics Service**: Regional performance metrics
- **Job Service**: Job location filtering

## Deployment

### Docker (Recommended)
```dockerfile
# Dockerfile provided in service directory
docker build -t location-service .
docker run -p 8001:8001 --env-file .env location-service
```

### Kubernetes
```yaml
# Deploy as part of recruitment platform microservices
kubectl apply -f k8s/location-service.yaml
```

### Cloud (AWS/Azure/GCP)
- Deploy as containerized service
- Connect to managed PostgreSQL (RDS/Azure DB/Cloud SQL)
- Configure environment variables via secrets manager

## Maintenance

### Database Updates
To update postcode data (e.g., annual ONS updates):
```bash
# Import new postcode data
python scripts/import_postcodes.py --file new_postcodes.csv
```

### Monitoring
Key metrics to monitor:
- Request latency (target: <100ms p95)
- Error rate (target: <1%)
- Database connection pool utilization
- Memory usage (pandas DataFrame operations)

## Support

For issues or questions:
- **ProActive People Ltd**: info@proactivepeople.com
- **Internal Docs**: See project root `docs_root/`
- **GitHub Issues**: (if applicable)

## License

Proprietary - ProActive People Ltd © 2025
