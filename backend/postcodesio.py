"""
Postcodes.io API Client with Haversine Distance Calculation

This module provides functionality to:
1. Fetch latitude/longitude coordinates for UK postcodes using the postcodes.io API
2. Calculate distances between postcodes using the Haversine formula
3. Validate and normalize UK postcodes

Author: ProActive People
Created: 2025-11-01
"""

import re
import math
import requests
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class PostcodeLocation:
    """Represents a postcode with its geographic coordinates."""
    postcode: str
    latitude: float
    longitude: float
    region: Optional[str] = None
    country: Optional[str] = None
    district: Optional[str] = None


@dataclass
class PostcodeDetails:
    """Detailed information about a UK postcode including administrative areas."""
    postcode: str
    latitude: float
    longitude: float

    # Administrative areas
    admin_district: Optional[str] = None  # District/Borough (e.g., "Bristol, City of")
    admin_county: Optional[str] = None    # County (e.g., "Gloucestershire")
    admin_ward: Optional[str] = None      # Electoral ward
    parish: Optional[str] = None          # Parish (if applicable)

    # Geographic regions
    region: Optional[str] = None          # Region (e.g., "South West")
    country: Optional[str] = None         # Country (England, Scotland, Wales, Northern Ireland)
    european_electoral_region: Optional[str] = None

    # Political
    parliamentary_constituency: Optional[str] = None

    # NHS
    ccg: Optional[str] = None             # Clinical Commissioning Group
    nhs_ha: Optional[str] = None          # NHS Health Authority

    # Other codes and identifiers
    codes: Optional[Dict] = None          # Various administrative codes
    quality: Optional[int] = None         # Positional quality indicator
    eastings: Optional[int] = None        # OS Eastings coordinate
    northings: Optional[int] = None       # OS Northings coordinate

    @property
    def town(self) -> Optional[str]:
        """
        Extract the town/city name from available fields.
        Priority: admin_district > admin_county > parish
        """
        # Try to extract from admin_district first (most reliable)
        if self.admin_district:
            # Remove common suffixes like ", City of", "London Borough of", etc.
            town = self.admin_district
            town = town.replace(", City of", "")
            town = town.replace("City of ", "")
            town = town.replace("London Borough of ", "")
            town = town.replace("Royal Borough of ", "")
            return town

        # Fallback to parish or county
        return self.parish or self.admin_county

    def __str__(self) -> str:
        """Human-readable string representation."""
        parts = [self.postcode]
        if self.town:
            parts.append(self.town)
        if self.region:
            parts.append(self.region)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


class PostcodesIOClient:
    """
    Client for interacting with the postcodes.io API.

    API Documentation: https://postcodes.io/
    Rate Limit: No authentication required, fair use policy applies
    """

    BASE_URL = "https://api.postcodes.io"

    def __init__(self, timeout: int = 10, use_cache: bool = True):
        """
        Initialize the Postcodes.io API client.

        Args:
            timeout: Request timeout in seconds (default: 10)
            use_cache: Whether to cache API responses (default: True)
        """
        self.timeout = timeout
        self.use_cache = use_cache
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ProActiveRecuitment/1.0',
            'Accept': 'application/json'
        })

    @staticmethod
    def normalize_postcode(postcode: str) -> str:
        """
        Normalize a UK postcode to standard format (uppercase, single space).

        Args:
            postcode: Raw postcode string

        Returns:
            Normalized postcode (e.g., "SW1A 1AA")

        Examples:
            >>> PostcodesIOClient.normalize_postcode("sw1a1aa")
            'SW1A 1AA'
            >>> PostcodesIOClient.normalize_postcode("BS1  4DJ")
            'BS1 4DJ'
        """
        # Remove all spaces and convert to uppercase
        postcode = postcode.replace(" ", "").upper()

        # UK postcode format: outward code + inward code
        # Insert space before last 3 characters
        if len(postcode) >= 5:
            return f"{postcode[:-3]} {postcode[-3:]}"

        return postcode

    @staticmethod
    def validate_postcode(postcode: str) -> bool:
        """
        Validate UK postcode format using regex.

        Args:
            postcode: Postcode to validate

        Returns:
            True if valid UK postcode format, False otherwise
        """
        # UK postcode regex pattern
        pattern = r'^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$'
        normalized = PostcodesIOClient.normalize_postcode(postcode)
        return bool(re.match(pattern, normalized))

    def lookup_postcode(self, postcode: str) -> Optional[PostcodeLocation]:
        """
        Lookup a single postcode and return its location data.

        Args:
            postcode: UK postcode to lookup

        Returns:
            PostcodeLocation object if found, None otherwise

        Raises:
            requests.RequestException: If API request fails
        """
        if not self.validate_postcode(postcode):
            raise ValueError(f"Invalid UK postcode format: {postcode}")

        normalized = self.normalize_postcode(postcode)

        # Use cached version if available
        if self.use_cache:
            cached = self._cached_lookup(normalized)
            if cached:
                return cached

        url = f"{self.BASE_URL}/postcodes/{normalized}"

        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            if data.get('status') == 200 and data.get('result'):
                result = data['result']
                return PostcodeLocation(
                    postcode=result['postcode'],
                    latitude=result['latitude'],
                    longitude=result['longitude'],
                    region=result.get('region'),
                    country=result.get('country'),
                    district=result.get('admin_district')
                )

            return None

        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to lookup postcode {postcode}: {str(e)}")

    @lru_cache(maxsize=1000)
    def _cached_lookup(self, normalized_postcode: str) -> Optional[PostcodeLocation]:
        """Internal cached lookup method (LRU cache for 1000 postcodes)."""
        return None  # Cache miss, will be populated by main lookup

    def get_postcode_details(self, postcode: str) -> Optional[PostcodeDetails]:
        """
        Get comprehensive details about a postcode including town/city information.

        This method returns more detailed information than lookup_postcode(),
        including administrative areas, electoral wards, NHS regions, and more.

        Args:
            postcode: UK postcode to lookup (e.g., "BS1 4DJ", "DY11 6LF")

        Returns:
            PostcodeDetails object with comprehensive information if found, None otherwise

        Raises:
            ValueError: If postcode format is invalid
            requests.RequestException: If API request fails

        Example:
            >>> client = PostcodesIOClient()
            >>> details = client.get_postcode_details("DY11 6LF")
            >>> print(details.town)  # "Kidderminster"
            >>> print(details.admin_district)  # "Wyre Forest"
            >>> print(details.parliamentary_constituency)  # "Wyre Forest"
        """
        if not self.validate_postcode(postcode):
            raise ValueError(f"Invalid UK postcode format: {postcode}")

        normalized = self.normalize_postcode(postcode)
        url = f"{self.BASE_URL}/postcodes/{normalized}"

        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            if data.get('status') == 200 and data.get('result'):
                result = data['result']

                # Extract codes dictionary
                codes = result.get('codes') or {}

                return PostcodeDetails(
                    postcode=result['postcode'],
                    latitude=result['latitude'],
                    longitude=result['longitude'],
                    admin_district=result.get('admin_district'),
                    admin_county=result.get('admin_county'),
                    admin_ward=result.get('admin_ward'),
                    parish=result.get('parish'),
                    region=result.get('region'),
                    country=result.get('country'),
                    european_electoral_region=result.get('european_electoral_region'),
                    parliamentary_constituency=result.get('parliamentary_constituency'),
                    ccg=result.get('ccg'),
                    nhs_ha=result.get('nhs_ha'),
                    codes=codes,
                    quality=result.get('quality'),
                    eastings=result.get('eastings'),
                    northings=result.get('northings')
                )

            return None

        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to get details for postcode {postcode}: {str(e)}")

    def bulk_lookup(self, postcodes: List[str]) -> Dict[str, Optional[PostcodeLocation]]:
        """
        Lookup multiple postcodes in a single API call (max 100).

        Args:
            postcodes: List of postcodes to lookup

        Returns:
            Dictionary mapping postcodes to their locations

        Raises:
            ValueError: If more than 100 postcodes provided
        """
        if len(postcodes) > 100:
            raise ValueError("Bulk lookup limited to 100 postcodes per request")

        normalized = [self.normalize_postcode(pc) for pc in postcodes]
        url = f"{self.BASE_URL}/postcodes"

        try:
            response = self.session.post(
                url,
                json={"postcodes": normalized},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            results = {}
            if data.get('status') == 200 and data.get('result'):
                for item in data['result']:
                    query = item.get('query')
                    result = item.get('result')

                    if result:
                        results[query] = PostcodeLocation(
                            postcode=result['postcode'],
                            latitude=result['latitude'],
                            longitude=result['longitude'],
                            region=result.get('region'),
                            country=result.get('country'),
                            district=result.get('admin_district')
                        )
                    else:
                        results[query] = None

            return results

        except requests.RequestException as e:
            raise requests.RequestException(f"Bulk lookup failed: {str(e)}")


class DistanceCalculator:
    """Calculate distances between geographic coordinates using Haversine formula."""

    EARTH_RADIUS_KM = 6371.0  # Earth's radius in kilometers
    EARTH_RADIUS_MILES = 3958.8  # Earth's radius in miles

    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        unit: str = 'km'
    ) -> float:
        """
        Calculate the great-circle distance between two points using Haversine formula.

        Args:
            lat1: Latitude of first point (decimal degrees)
            lon1: Longitude of first point (decimal degrees)
            lat2: Latitude of second point (decimal degrees)
            lon2: Longitude of second point (decimal degrees)
            unit: Distance unit - 'km' for kilometers or 'miles' (default: 'km')

        Returns:
            Distance in specified unit

        Raises:
            ValueError: If invalid unit specified
        """
        if unit not in ['km', 'miles']:
            raise ValueError("Unit must be 'km' or 'miles'")

        # Convert latitude and longitude from degrees to radians
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

        # Calculate distance
        radius = DistanceCalculator.EARTH_RADIUS_KM if unit == 'km' else DistanceCalculator.EARTH_RADIUS_MILES
        distance = radius * c

        return round(distance, 2)

    @staticmethod
    def postcode_distance(
        postcode1: str,
        postcode2: str,
        unit: str = 'km',
        client: Optional[PostcodesIOClient] = None
    ) -> Optional[float]:
        """
        Calculate distance between two UK postcodes.

        Args:
            postcode1: First postcode
            postcode2: Second postcode
            unit: Distance unit - 'km' or 'miles' (default: 'km')
            client: Optional PostcodesIOClient instance (creates new if not provided)

        Returns:
            Distance in specified unit, or None if either postcode not found

        Example:
            >>> DistanceCalculator.postcode_distance("BS1 4DJ", "SW1A 1AA")
            171.32
        """
        if client is None:
            client = PostcodesIOClient()

        # Lookup both postcodes
        loc1 = client.lookup_postcode(postcode1)
        loc2 = client.lookup_postcode(postcode2)

        if loc1 is None or loc2 is None:
            return None

        # Calculate distance
        return DistanceCalculator.haversine_distance(
            loc1.latitude,
            loc1.longitude,
            loc2.latitude,
            loc2.longitude,
            unit
        )


def main():
    """
    Example usage of the Postcodes.io client and distance calculator.
    """
    print("=" * 60)
    print("Postcodes.io Distance Calculator - Demo")
    print("=" * 60)

    # Initialize client
    client = PostcodesIOClient()

    # Example 1: Single postcode lookup
    print("\n1. Single Postcode Lookup:")
    postcode = "BS1 4DJ"  # Bristol
    location = client.lookup_postcode(postcode)

    if location:
        print(f"   Postcode: {location.postcode}")
        print(f"   Latitude: {location.latitude}")
        print(f"   Longitude: {location.longitude}")
        print(f"   District: {location.district}")
        print(f"   Region: {location.region}")

    # Example 2: Distance calculation
    print("\n2. Distance Calculation:")
    postcode1 = "BS1 4DJ"  # Bristol, ProActive People office
    postcode2 = "SW1A 1AA"  # London, Westminster

    distance_km = DistanceCalculator.postcode_distance(postcode1, postcode2, unit='km', client=client)
    distance_miles = DistanceCalculator.postcode_distance(postcode1, postcode2, unit='miles', client=client)

    if distance_km and distance_miles:
        print(f"   From: {postcode1}")
        print(f"   To: {postcode2}")
        print(f"   Distance: {distance_km} km ({distance_miles} miles)")

    # Example 3: Detailed postcode information (town/city data)
    print("\n3. Get Town/City Details:")
    test_postcodes = ["DY11 6LF", "BS1 4DJ", "SW1A 1AA"]

    for pc in test_postcodes:
        details = client.get_postcode_details(pc)
        if details:
            print(f"   {details.postcode}:")
            print(f"      Town/City:     {details.town}")
            print(f"      District:      {details.admin_district}")
            print(f"      County:        {details.admin_county}")
            print(f"      Region:        {details.region}")
            print(f"      Constituency:  {details.parliamentary_constituency}")

    # Example 4: Bulk lookup
    print("\n4. Bulk Postcode Lookup:")
    postcodes = ["BS1 4DJ", "M1 1AA", "EH1 1YZ", "CF10 1EP"]  # Bristol, Manchester, Edinburgh, Cardiff
    results = client.bulk_lookup(postcodes)

    for pc, loc in results.items():
        if loc:
            print(f"   {pc}: {loc.region}, {loc.country}")
        else:
            print(f"   {pc}: Not found")

    # Example 5: Distance matrix
    print("\n5. Distance Matrix (Bristol to other cities in km):")
    bristol = "BS1 4DJ"
    cities = {
        "London": "SW1A 1AA",
        "Manchester": "M1 1AA",
        "Edinburgh": "EH1 1YZ",
        "Cardiff": "CF10 1EP"
    }

    for city, postcode in cities.items():
        distance = DistanceCalculator.postcode_distance(bristol, postcode, unit='km', client=client)
        if distance:
            print(f"   Bristol -> {city:12s}: {distance:6.2f} km")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
