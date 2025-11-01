# Location Service - Implementation Guide

## Summary

Successfully adapted `backend-api/postcodes.py` to work as a proper microservice within the ProActive People recruitment platform architecture.

## What Was Done

### 1. Created Proper Service Structure

Created a new `location-service` microservice in [backend/services/location-service/](backend/services/location-service/) following the project's microservices architecture:

```
backend/services/location-service/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── postcodes.py        # Database models (Postcodes, Demographics)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── postcodes.py        # API endpoints (adapted from original)
│   └── utils/
│       ├── __init__.py
│       └── postcode_utils.py   # Postcode extraction & parsing utilities
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive documentation
├── .env.example                # Configuration template
└── start.bat                   # Windows startup script
```

### 2. Fixed Import Issues

**Original Code Issues:**
```python
# ❌ Original imports (broken)
from backend.db.models import Demographics, Postcodes
from backend.db.database import get_db
```

**Fixed Imports:**
```python
# ✅ Correct imports for new structure
from ..models import Postcodes, Demographics
from ..db import get_db
from ..utils.postcode_utils import (
    extract_uk_postcode_from_string,
    extract_uk_postcode_from_string_flexible,
    # ... other utilities
)
```

### 3. Created Database Infrastructure

#### [src/db/database.py](backend/services/location-service/src/db/database.py)
- SQLAlchemy engine configuration
- Connection pooling (configurable via .env)
- Session factory and dependency injection
- Database initialization functions
- Health check functionality

#### [src/models/postcodes.py](backend/services/location-service/src/models/postcodes.py)
- `Postcodes` model: UK postcode data with coordinates
- `Demographics` model: Socioeconomic data by postcode sector
- Proper indexes for performance
- `to_dict()` methods for JSON serialization

### 4. Adapted Routes & Endpoints

#### [src/routes/postcodes.py](backend/services/location-service/src/routes/postcodes.py)

Migrated all functionality from original `postcodes.py`:

| Endpoint | Method | Description | Original | Status |
|----------|--------|-------------|----------|--------|
| `/api/postcodes/{postcode}` | GET | Single postcode lookup | ✅ | ✅ Migrated |
| `/api/postcodes/batch` | POST | Batch postcode lookup | ✅ | ✅ Migrated |
| `/api/postcodes/search/{pattern}` | GET | Wildcard postcode search | ✅ | ✅ Migrated |
| `/api/postcodes/upload/csv` | POST | CSV processing with extraction | ✅ | ✅ Migrated |
| `/api/postcodes/health` | GET | Health check | ❌ | ✅ Added |

**Improvements Made:**
- ✅ Proper Pydantic request/response models
- ✅ Better error handling with appropriate HTTP status codes
- ✅ Comprehensive logging throughout
- ✅ Type hints for better IDE support
- ✅ Async/await for FastAPI best practices
- ✅ Input validation and sanitization

### 5. Enhanced Utilities

#### [src/utils/postcode_utils.py](backend/services/location-service/src/utils/postcode_utils.py)

Extracted and enhanced postcode utility functions:
- `extract_uk_postcode_from_string()` - Extract with space required
- `extract_uk_postcode_from_string_flexible()` - Extract with missing space handling
- `extract_postcode_sector()` - Get sector from full postcode
- `extract_postcode_district()` - Get district from full postcode
- `extract_postcode_area()` - Get area from full postcode
- `normalize_postcode()` - Standardize format
- `validate_uk_postcode()` - Format validation

### 6. Created FastAPI Application

#### [src/main.py](backend/services/location-service/src/main.py)

Complete FastAPI application with:
- Lifespan context manager for startup/shutdown
- CORS middleware configuration
- Request timing middleware
- Global exception handling
- Service health check endpoints
- Automatic API documentation (Swagger/ReDoc)

### 7. Configuration & Documentation

- **[requirements.txt](backend/services/location-service/requirements.txt)**: All Python dependencies with versions
- **[README.md](backend/services/location-service/README.md)**: 350+ line comprehensive guide
- **[.env.example](backend/services/location-service/.env.example)**: Configuration template
- **[start.bat](backend/services/location-service/start.bat)**: Windows startup script

## Key Improvements Over Original

| Aspect | Original | New Implementation |
|--------|----------|-------------------|
| **Structure** | Single file in wrong directory | Proper microservice structure |
| **Imports** | Broken paths | Correct relative imports |
| **Database** | Assumed `backend.db` module | Self-contained database setup |
| **Error Handling** | Basic try/catch | Comprehensive with proper HTTP codes |
| **Documentation** | Minimal inline comments | Full README + docstrings |
| **Type Safety** | Limited | Pydantic models + type hints |
| **Testing** | None | Ready for pytest integration |
| **Configuration** | Hardcoded values | Environment variables |
| **Logging** | print() statements | Proper logging module |
| **CORS** | Not configured | Middleware with .env control |

## Database Schema

### `postcodes` Table
```sql
CREATE TABLE postcodes (
    id SERIAL PRIMARY KEY,
    postcode VARCHAR(10) UNIQUE NOT NULL,
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL,
    town VARCHAR(100),
    county VARCHAR(100)
);

-- Indexes for performance
CREATE INDEX idx_postcode_town ON postcodes(town);
CREATE INDEX idx_postcode_county ON postcodes(county);
CREATE INDEX idx_postcode_coordinates ON postcodes(lat, lng);
```

### `demographics` Table
```sql
CREATE TABLE demographics (
    id SERIAL PRIMARY KEY,
    postcode_sector VARCHAR(10) UNIQUE NOT NULL,
    population INTEGER,
    social_grade_ab FLOAT,
    social_grade_c1 FLOAT,
    social_grade_c2 FLOAT,
    social_grade_de FLOAT,
    median_income FLOAT,
    employment_rate FLOAT,
    data_source VARCHAR(100)
);
```

## How to Use

### 1. Install Dependencies
```bash
cd backend/services/location-service
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Use project root .env or create service-specific .env
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Start the Service

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
python -m src.main
```

**With Hot Reload (Development):**
```bash
uvicorn src.main:app --reload --port 8001
```

### 4. Access API Documentation
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

### 5. Test Endpoints

```bash
# Single postcode lookup
curl http://localhost:8001/api/postcodes/BS1%204DJ

# Batch lookup
curl -X POST http://localhost:8001/api/postcodes/batch \
  -H "Content-Type: application/json" \
  -d '{"postcodes": ["BS1 4DJ", "BS2 0JA"]}'

# Search
curl http://localhost:8001/api/postcodes/search/BS1?limit=50

# CSV upload
curl -X POST http://localhost:8001/api/postcodes/upload/csv?records=100 \
  -F "file=@data.csv"
```

## Integration with Existing Services

### From Node.js Backend (Express/NestJS)
```javascript
const axios = require('axios');

// Single lookup
const postcode = await axios.get('http://localhost:8001/api/postcodes/BS1 4DJ');
console.log(postcode.data);

// Batch lookup
const batch = await axios.post('http://localhost:8001/api/postcodes/batch', {
  postcodes: ['BS1 4DJ', 'BS2 0JA', 'BS3 1HL']
});
console.log(batch.data);
```

### From Python AI Router
```python
import httpx

async def get_postcode_data(postcode: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8001/api/postcodes/{postcode}"
        )
        return response.json()
```

### From Frontend (React/Next.js)
```typescript
// Single lookup
const response = await fetch('http://localhost:8001/api/postcodes/BS1%204DJ');
const data = await response.json();

// Batch lookup
const batchResponse = await fetch('http://localhost:8001/api/postcodes/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ postcodes: ['BS1 4DJ', 'BS2 0JA'] })
});
const batchData = await batchResponse.json();
```

## Next Steps

### Immediate (Phase 1)
1. ✅ Service structure created
2. ✅ Database models defined
3. ✅ API endpoints implemented
4. ⏳ **Test service locally**
5. ⏳ **Import postcode data into PostgreSQL**

### Short-term (Phase 2)
6. ⏳ Add unit tests (pytest)
7. ⏳ Add integration tests
8. ⏳ Set up Docker container
9. ⏳ Configure in API Gateway routing

### Medium-term (Phase 3)
10. ⏳ Import demographics data
11. ⏳ Add caching layer (Redis)
12. ⏳ Implement rate limiting
13. ⏳ Add monitoring/metrics

### Long-term (Phase 4)
14. ⏳ Deploy to staging
15. ⏳ Performance optimization
16. ⏳ Load testing
17. ⏳ Production deployment

## Testing Checklist

### Manual Testing
- [ ] Service starts successfully
- [ ] Database connection works
- [ ] `/health` endpoint returns 200
- [ ] Single postcode lookup works
- [ ] Batch lookup works (3+ postcodes)
- [ ] Search with pattern works
- [ ] CSV upload processes correctly
- [ ] Error handling for invalid postcode
- [ ] Swagger docs accessible

### Unit Tests (To Be Created)
```bash
# Test structure:
tests/
├── __init__.py
├── conftest.py              # pytest fixtures
├── test_database.py         # Database connection tests
├── test_models.py           # Model validation tests
├── test_postcode_utils.py   # Utility function tests
└── test_routes.py           # API endpoint tests
```

### Integration Tests (To Be Created)
- End-to-end postcode lookup flow
- CSV processing with real data
- Database query performance
- Error scenarios

## Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Single Lookup | <10ms | 95th percentile |
| Batch Lookup (100) | <50ms | 95th percentile |
| CSV Processing (1000 rows) | <500ms | Average |
| Search (pattern) | <100ms | With limit=100 |

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOCATION_SERVICE_PORT` | No | 8001 | Service port |
| `LOCATION_SERVICE_HOST` | No | 0.0.0.0 | Service host |
| `POSTGRES_HOST` | Yes | localhost | PostgreSQL host |
| `POSTGRES_PORT` | No | 5432 | PostgreSQL port |
| `POSTGRES_DB` | Yes | recruitment | Database name |
| `POSTGRES_USER` | Yes | admin | Database user |
| `POSTGRES_PASSWORD` | Yes | - | Database password |
| `POSTGRES_POOL_MIN` | No | 2 | Min connections |
| `POSTGRES_POOL_MAX` | No | 10 | Max connections |
| `CORS_ORIGINS` | No | * | Allowed origins |
| `NODE_ENV` | No | development | Environment |

## Troubleshooting

### Service won't start
```bash
# Check PostgreSQL is running
psql -h localhost -U admin -d recruitment

# Check port 8001 is available
netstat -an | findstr 8001

# Check Python version
python --version  # Should be 3.10+
```

### Database connection fails
```bash
# Verify credentials in .env
cat .env | grep POSTGRES

# Test connection manually
psql -h localhost -U admin -d recruitment -c "SELECT 1"
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

## Migration from Old Code

The original `backend-api/postcodes.py` has been preserved as `backend-api/postcodes.py.old` for reference.

**Key Changes:**
1. Module structure: Flat file → Microservice with src/ layout
2. Imports: `backend.db.*` → Relative imports from `src/`
3. Database setup: External dependency → Self-contained in `src/db/`
4. Error handling: Basic → Comprehensive with proper HTTP codes
5. Configuration: Mixed → Environment variables via .env

## Support & Maintenance

- **Documentation**: See [README.md](backend/services/location-service/README.md)
- **API Docs**: http://localhost:8001/docs (when running)
- **Contact**: ProActive People development team

## Related Documentation

- Project root [CLAUDE.md](../../../CLAUDE.md) - Project overview
- [.env.example](../../../.env.example) - Global configuration
- [backend/services/](../) - Other microservices

---

**Implementation Date**: 2025-01-15
**Author**: Claude Code
**Status**: ✅ Complete - Ready for Testing
