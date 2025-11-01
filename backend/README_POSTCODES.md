# Postcodes.io Distance Calculator

Comprehensive UK postcode lookup and distance calculation system using the [postcodes.io API](https://postcodes.io/) and the Haversine formula.

## Files

- **[postcodesio.py](postcodesio.py)** - Main module with API client and distance calculator
- **[test_postcodesio_cli.py](test_postcodesio_cli.py)** - CLI testing tool with interactive and batch modes
- **[example_town_lookup.py](example_town_lookup.py)** - Example script demonstrating town/city lookup

## Features

### PostcodesIOClient
- ✅ Single postcode lookup with full location data
- ✅ **Detailed postcode information including town/city names**
- ✅ Bulk lookup (up to 100 postcodes per request)
- ✅ Postcode validation and normalization
- ✅ LRU caching for 1000 most recent lookups
- ✅ Comprehensive error handling

### PostcodeDetails
- ✅ **Automatic town/city name extraction**
- ✅ Administrative areas (district, county, ward, parish)
- ✅ Geographic regions (region, country)
- ✅ Political information (parliamentary constituency)
- ✅ NHS regions (CCG, Health Authority)
- ✅ OS coordinates (eastings, northings)

### DistanceCalculator
- ✅ Haversine distance calculation (great-circle distance)
- ✅ Support for kilometers and miles
- ✅ Direct postcode-to-postcode distance calculation
- ✅ High precision (accurate to 2 decimal places)

## Installation

```bash
pip install requests
```

## Quick Start

### Python API Usage

```python
from postcodesio import PostcodesIOClient, DistanceCalculator

# Initialize client
client = PostcodesIOClient()

# Get detailed postcode information including town/city
details = client.get_postcode_details("DY11 6LF")
print(f"Town: {details.town}")  # Output: "Wyre Forest"
print(f"District: {details.admin_district}")  # Output: "Wyre Forest"
print(f"County: {details.admin_county}")  # Output: "Worcestershire"
print(f"Constituency: {details.parliamentary_constituency}")  # Output: "Wyre Forest"

# Lookup a single postcode (basic info)
location = client.lookup_postcode("BS1 4DJ")
print(f"{location.postcode}: {location.latitude}, {location.longitude}")

# Calculate distance between two postcodes
distance_km = DistanceCalculator.postcode_distance(
    "BS1 4DJ",   # Bristol (ProActive People office)
    "SW1A 1AA",  # London
    unit='km'
)
print(f"Distance: {distance_km} km")  # Output: 170.13 km

# Bulk lookup
postcodes = ["BS1 4DJ", "M1 1AA", "EH1 1YZ", "CF10 1EP"]
results = client.bulk_lookup(postcodes)
for postcode, location in results.items():
    if location:
        print(f"{postcode}: {location.region}, {location.country}")
```

### CLI Testing Tool

#### Interactive Mode
```bash
python test_postcodesio_cli.py
```

This launches an interactive menu:
```
  Options:
  1. Lookup single postcode
  2. Get detailed postcode information (town/city data)
  3. Calculate distance between two postcodes
  4. Bulk lookup multiple postcodes
  5. Distance matrix (one to many)
  6. Run comprehensive test suite
  0. Exit
```

#### Command-Line Arguments

**Single Postcode Lookup:**
```bash
python test_postcodesio_cli.py --lookup "BS1 4DJ"
```

**Detailed Postcode Information (Town/City):**
```bash
python test_postcodesio_cli.py --details "DY11 6LF"
```

**Distance Calculation:**
```bash
python test_postcodesio_cli.py --postcode1 "BS1 4DJ" --postcode2 "SW1A 1AA"
```

**Bulk Lookup:**
```bash
python test_postcodesio_cli.py --bulk "BS1 4DJ,SW1A 1AA,M1 1AA,CF10 1EP"
```

**Distance Matrix:**
```bash
python test_postcodesio_cli.py --matrix "BS1 4DJ" --targets "SW1A 1AA,CF10 1EP,EH1 1YZ"
```

**Comprehensive Test Suite:**
```bash
python test_postcodesio_cli.py --test-suite
```

**Distance in Miles:**
```bash
python test_postcodesio_cli.py --postcode1 "BS1 4DJ" --postcode2 "SW1A 1AA" --unit miles
```

## API Reference

### PostcodesIOClient

#### `__init__(timeout=10, use_cache=True)`
Initialize the client.
- `timeout` - Request timeout in seconds (default: 10)
- `use_cache` - Enable LRU caching (default: True)

#### `lookup_postcode(postcode: str) -> Optional[PostcodeLocation]`
Lookup a single postcode.
- Returns `PostcodeLocation` object if found, `None` otherwise
- Raises `ValueError` for invalid postcode format
- Raises `requests.RequestException` for API errors

#### `get_postcode_details(postcode: str) -> Optional[PostcodeDetails]`
Get comprehensive details about a postcode including town/city information.
- Returns `PostcodeDetails` object with full administrative data if found, `None` otherwise
- Includes automatic town/city name extraction via the `.town` property
- Raises `ValueError` for invalid postcode format
- Raises `requests.RequestException` for API errors

Example:
```python
details = client.get_postcode_details("DY11 6LF")
print(details.town)  # "Wyre Forest"
print(details.admin_district)  # "Wyre Forest"
print(details.parliamentary_constituency)  # "Wyre Forest"
```

#### `bulk_lookup(postcodes: List[str]) -> Dict[str, Optional[PostcodeLocation]]`
Lookup multiple postcodes (max 100 per request).
- Returns dictionary mapping postcodes to locations
- Raises `ValueError` if more than 100 postcodes provided

#### `normalize_postcode(postcode: str) -> str`
Normalize postcode to standard format (uppercase, single space).

#### `validate_postcode(postcode: str) -> bool`
Validate UK postcode format using regex.

### DistanceCalculator

#### `haversine_distance(lat1, lon1, lat2, lon2, unit='km') -> float`
Calculate great-circle distance between two coordinates.
- `lat1`, `lon1` - First point (decimal degrees)
- `lat2`, `lon2` - Second point (decimal degrees)
- `unit` - 'km' or 'miles' (default: 'km')
- Returns distance rounded to 2 decimal places

#### `postcode_distance(postcode1, postcode2, unit='km', client=None) -> Optional[float]`
Calculate distance between two postcodes.
- `postcode1`, `postcode2` - UK postcodes
- `unit` - 'km' or 'miles' (default: 'km')
- `client` - Optional PostcodesIOClient instance
- Returns distance or `None` if either postcode not found

### PostcodeLocation (Dataclass)

Basic postcode location information.

```python
@dataclass
class PostcodeLocation:
    postcode: str
    latitude: float
    longitude: float
    region: Optional[str] = None
    country: Optional[str] = None
    district: Optional[str] = None
```

### PostcodeDetails (Dataclass)

Comprehensive postcode information with automatic town/city extraction.

```python
@dataclass
class PostcodeDetails:
    postcode: str
    latitude: float
    longitude: float

    # Administrative areas
    admin_district: Optional[str] = None
    admin_county: Optional[str] = None
    admin_ward: Optional[str] = None
    parish: Optional[str] = None

    # Geographic regions
    region: Optional[str] = None
    country: Optional[str] = None
    european_electoral_region: Optional[str] = None

    # Political
    parliamentary_constituency: Optional[str] = None

    # NHS
    ccg: Optional[str] = None  # Clinical Commissioning Group
    nhs_ha: Optional[str] = None  # NHS Health Authority

    # Other
    codes: Optional[Dict] = None
    quality: Optional[int] = None
    eastings: Optional[int] = None
    northings: Optional[int] = None

    @property
    def town(self) -> Optional[str]:
        """Extract town/city name from admin_district, parish, or county."""
```

## Example Results

### ProActive People Office (Bristol) Distances:
- Bristol → London: **170.13 km** (105.71 miles)
- Bristol → Cardiff: **40.43 km** (25.12 miles)
- Bristol → Edinburgh: **501.75 km** (311.78 miles)

## Use Cases in Recruitment System

### 1. Town/City Matching
```python
# Check if candidate and job are in the same town/city
candidate_postcode = "BS1 4DJ"
job_postcode = "BS2 0JA"

candidate_details = client.get_postcode_details(candidate_postcode)
job_details = client.get_postcode_details(job_postcode)

if candidate_details.town == job_details.town:
    print(f"Match! Both in {candidate_details.town}")
    print(f"Constituency: {candidate_details.parliamentary_constituency}")
```

### 2. Candidate-Job Distance Matching
```python
# Calculate commute distance for candidate evaluation
candidate_postcode = "BS1 4DJ"
job_postcode = "CF10 1EP"

distance = DistanceCalculator.postcode_distance(candidate_postcode, job_postcode)

if distance and distance < 50:  # Within 50km
    print("Suitable commute distance")
```

### 3. Radius Search
```python
# Find candidates within 30km of job location
job_location = client.lookup_postcode("BS1 4DJ")
candidates = get_candidates_from_database()

nearby_candidates = []
for candidate in candidates:
    candidate_loc = client.lookup_postcode(candidate.postcode)
    if candidate_loc:
        distance = DistanceCalculator.haversine_distance(
            job_location.latitude, job_location.longitude,
            candidate_loc.latitude, candidate_loc.longitude
        )
        if distance <= 30:
            nearby_candidates.append((candidate, distance))

# Sort by distance
nearby_candidates.sort(key=lambda x: x[1])
```

### 4. Branch Coverage Analysis
```python
# Calculate coverage area for Bristol office
office_postcode = "BS1 4DJ"
client_postcodes = ["CF10 1EP", "SW1A 1AA", "B1 1AA"]

for client_pc in client_postcodes:
    distance = DistanceCalculator.postcode_distance(office_postcode, client_pc)
    if distance:
        print(f"Client {client_pc}: {distance} km from Bristol office")
```

### 5. Placement Analytics
```python
# Calculate average commute distance for placements
placements = get_placements_from_database()

total_distance = 0
count = 0

for placement in placements:
    distance = DistanceCalculator.postcode_distance(
        placement.candidate_postcode,
        placement.job_postcode
    )
    if distance:
        total_distance += distance
        count += 1

average_commute = total_distance / count if count > 0 else 0
print(f"Average commute distance: {average_commute:.2f} km")
```

## Performance

- **API Response Time**: ~100-300ms per request
- **Haversine Calculation**: <1ms
- **Bulk Lookup**: ~200-500ms for 100 postcodes
- **Caching**: LRU cache stores 1000 most recent lookups

## Error Handling

The module includes comprehensive error handling:

```python
try:
    location = client.lookup_postcode("INVALID")
except ValueError as e:
    print(f"Invalid postcode format: {e}")
except requests.RequestException as e:
    print(f"API request failed: {e}")
```

## API Limits

- The postcodes.io API is free and requires no authentication
- Fair use policy applies (no hard rate limits documented)
- Bulk lookup limited to 100 postcodes per request
- Consider implementing rate limiting for production use

## Testing

Run the demo script:
```bash
python postcodesio.py
```

Run the comprehensive CLI test suite:
```bash
python test_postcodesio_cli.py --test-suite
```

## Dependencies

- `requests` - HTTP library for API calls
- `math` - Standard library for Haversine calculations
- `re` - Standard library for postcode validation
- `dataclasses` - Standard library for data structures
- `functools` - Standard library for LRU caching

## License

Part of ProActive People Recruitment Automation System.

## Support

For issues or questions, contact:
- ProActive People Ltd.
- 📞 0117 9377 199
- 📧 info@proactivepeople.com
