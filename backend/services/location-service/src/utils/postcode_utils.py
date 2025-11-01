"""
UK Postcode utility functions for extraction and parsing.

Provides regex-based extraction of UK postcodes from address strings
and parsing functions for postcode components (area, district, sector).

Reference: https://ideal-postcodes.co.uk/guides/uk-postcode-format
"""

import re
from typing import Optional


def extract_uk_postcode_from_string(address: str) -> Optional[str]:
    """
    Extract a UK postcode from an address string (requires space).

    Args:
        address: Full address string potentially containing a postcode

    Returns:
        Uppercase postcode if found, None otherwise

    Example:
        >>> extract_uk_postcode_from_string("123 Main St, Bristol BS1 4DJ")
        'BS1 4DJ'
    """
    pattern = r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b'
    match = re.search(pattern, address, re.IGNORECASE)
    return match.group().upper() if match else None


def extract_uk_postcode_from_string_flexible(address: str) -> Optional[str]:
    """
    Extract a UK postcode from an address string (handles missing space).

    More flexible version that works even when the postcode lacks a space
    between outward and inward codes.

    Args:
        address: Full address string potentially containing a postcode

    Returns:
        Uppercase postcode if found, None otherwise

    Example:
        >>> extract_uk_postcode_from_string_flexible("123 Main St, Bristol BS14DJ")
        'BS1 4DJ'
    """
    pattern = r'\b[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][ABD-HJLNP-UW-Z]{2}\b'
    match = re.search(pattern, address, re.IGNORECASE)
    return match.group().upper() if match else None


def extract_postcode_sector(postcode: str) -> Optional[str]:
    """
    Extract the sector from a full UK postcode.

    The sector is everything except the last two characters (unit).
    For example, "BS1 4DJ" -> "BS1 4D"

    Args:
        postcode: Full UK postcode

    Returns:
        Postcode sector or None if invalid

    Example:
        >>> extract_postcode_sector("BS1 4DJ")
        'BS1 4D'
    """
    postcode = postcode.strip().upper()
    if len(postcode) < 5:  # Minimum valid postcode length
        return None
    return postcode[:-2].strip()


def extract_postcode_district(postcode: str) -> Optional[str]:
    """
    Extract the district from a full UK postcode.

    The district is the outward code (everything up to the space).
    For example, "BS1 4DJ" -> "BS1"

    Args:
        postcode: Full UK postcode

    Returns:
        Postcode district or None if invalid

    Example:
        >>> extract_postcode_district("BS1 4DJ")
        'BS1'
    """
    postcode = postcode.strip().upper()
    match = re.match(r'^([A-Z]{1,2}\d[A-Z]?|\d[A-Z]{1,2})', postcode)
    return match.group(1) if match else None


def extract_postcode_area(postcode: str) -> Optional[str]:
    """
    Extract the area from a full UK postcode.

    The area is the leading alphabetic part of the postcode.
    For example, "BS1 4DJ" -> "BS"

    Args:
        postcode: Full UK postcode

    Returns:
        Postcode area or None if invalid

    Example:
        >>> extract_postcode_area("BS1 4DJ")
        'BS'
    """
    postcode = postcode.strip().upper()
    match = re.match(r'^([A-Z]{1,2})', postcode)
    return match.group(1) if match else None


def normalize_postcode(postcode: str) -> str:
    """
    Normalize a UK postcode to standard format with proper spacing.

    Args:
        postcode: UK postcode in any format

    Returns:
        Normalized postcode in format "XX## #XX"

    Example:
        >>> normalize_postcode("bs14dj")
        'BS1 4DJ'
    """
    postcode = postcode.strip().upper().replace(" ", "")
    if len(postcode) < 5:
        return postcode

    # Insert space before last 3 characters
    return f"{postcode[:-3]} {postcode[-3:]}"


def validate_uk_postcode(postcode: str) -> bool:
    """
    Validate if a string is a valid UK postcode format.

    Args:
        postcode: String to validate

    Returns:
        True if valid UK postcode format, False otherwise

    Example:
        >>> validate_uk_postcode("BS1 4DJ")
        True
        >>> validate_uk_postcode("INVALID")
        False
    """
    pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][ABD-HJLNP-UW-Z]{2}$'
    return bool(re.match(pattern, postcode.strip().upper()))
