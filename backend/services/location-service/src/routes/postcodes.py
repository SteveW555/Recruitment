"""
FastAPI routes for UK postcode operations.

Provides endpoints for:
- Single and batch postcode lookups
- CSV file processing with postcode extraction
- Postcode search functionality
"""

import csv
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
import sqlalchemy
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import traceback
import logging
import io

from ..models import Postcodes, Demographics
from ..db import get_db
from ..utils.postcode_utils import (
    extract_uk_postcode_from_string,
    extract_uk_postcode_from_string_flexible,
    extract_postcode_sector,
    extract_postcode_district,
    extract_postcode_area,
)
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/postcodes", tags=["Postcodes"])


# ===== Pydantic Request/Response Models =====

class PostcodesBatchRequest(BaseModel):
    """Request model for batch postcode lookup."""
    postcodes: List[str]


class PostcodeResponse(BaseModel):
    """Response model for single postcode data."""
    postcode: str
    lat: float
    lng: float
    town: str
    county: str


class CSVUploadResponse(BaseModel):
    """Response model for CSV upload processing."""
    column_names: List[str]
    data: List[Dict[str, Any]]
    records_returned: int
    total_records: int


# ===== Single Postcode Lookup =====

@router.get("/{postcode}", response_model=PostcodeResponse)
async def get_postcode_data(postcode: str, db: Session = Depends(get_db)):
    """
    Get geographic data for a single UK postcode.

    Args:
        postcode: UK postcode (e.g., "BS1 4DJ")
        db: Database session (injected)

    Returns:
        PostcodeResponse: Postcode data including coordinates, town, county

    Raises:
        HTTPException: 404 if postcode not found
    """
    logger.info(f"Looking up postcode: {postcode}")

    try:
        stmt = sqlalchemy.select(Postcodes).where(Postcodes.postcode == postcode.upper())
        result = db.execute(stmt).first()

        if result:
            postcode_data = result[0]
            logger.info(f"Postcode found: {postcode}")
            return {
                'postcode': postcode_data.postcode,
                'lat': float(postcode_data.lat),
                'lng': float(postcode_data.lng),
                'town': postcode_data.town,
                'county': postcode_data.county
            }
        else:
            logger.warning(f"Postcode not found: {postcode}")
            raise HTTPException(status_code=404, detail=f"Postcode '{postcode}' not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving postcode: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ===== Batch Postcode Lookup =====

@router.post("/batch", response_model=Dict[str, PostcodeResponse])
async def get_postcodes_batch(
    request: PostcodesBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Get geographic data for multiple UK postcodes in a single request.

    Args:
        request: Batch request containing list of postcodes
        db: Database session (injected)

    Returns:
        Dict mapping postcodes to their data

    Example:
        Request: {"postcodes": ["BS1 4DJ", "BS2 0JA"]}
        Response: {
            "BS1 4DJ": {"postcode": "BS1 4DJ", "lat": 51.45, "lng": -2.59, ...},
            "BS2 0JA": {"postcode": "BS2 0JA", "lat": 51.46, "lng": -2.58, ...}
        }
    """
    postcodes = [pc.upper() for pc in request.postcodes]
    logger.info(f"Batch lookup for {len(postcodes)} postcodes")

    try:
        stmt = sqlalchemy.select(Postcodes).where(Postcodes.postcode.in_(postcodes))
        results = db.execute(stmt).fetchall()

        postcode_data = {}
        for result in results:
            pc = result[0]
            postcode_data[pc.postcode] = {
                'postcode': pc.postcode,
                'lat': float(pc.lat),
                'lng': float(pc.lng),
                'town': pc.town,
                'county': pc.county
            }

        logger.info(f"Found {len(postcode_data)}/{len(postcodes)} postcodes")

        if not postcode_data:
            raise HTTPException(status_code=404, detail="No postcodes found")

        return postcode_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch lookup: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ===== Postcode Search =====

@router.get("/search/{pattern}")
async def search_postcodes(pattern: str, db: Session = Depends(get_db), limit: int = Query(default=100, le=1000)):
    """
    Search for postcodes matching a pattern (wildcard search).

    Args:
        pattern: Search pattern (e.g., "BS1" finds all BS1 postcodes)
        db: Database session (injected)
        limit: Maximum results to return (default 100, max 1000)

    Returns:
        List of matching postcode records

    Example:
        GET /api/postcodes/search/BS1?limit=50
    """
    logger.info(f"Searching postcodes with pattern: {pattern}")

    try:
        query = db.query(Postcodes)
        search = f"%{pattern.upper()}%"
        results = query.filter(Postcodes.postcode.ilike(search)).limit(limit).all()

        # Use SQLAlchemy's inspect to get column information
        inspector = sqlalchemy.inspect(Postcodes)
        columns = [column.key for column in inspector.columns]

        matches = [
            {column: getattr(pc, column) for column in columns}
            for pc in results
        ]

        logger.info(f"Found {len(matches)} matching postcodes")
        return {
            "pattern": pattern,
            "matches": len(matches),
            "limit": limit,
            "results": matches
        }

    except Exception as e:
        logger.error(f"Error searching postcodes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ===== CSV Processing =====

@router.post("/upload/csv", response_model=CSVUploadResponse)
async def process_csv_with_postcodes(
    file: UploadFile = File(...),
    records: int = Query(default=100, ge=1, le=10000)
):
    """
    Upload a CSV file, extract postcodes from any column, and return processed data.

    The endpoint:
    1. Scans all columns for UK postcodes
    2. Adds a 'postcode' column as the first column
    3. Handles missing spaces in postcodes
    4. Returns the processed data with column names

    Args:
        file: CSV file upload
        records: Number of records to return (default 100, max 10000)

    Returns:
        CSVUploadResponse with processed data

    Example:
        POST /api/postcodes/upload/csv?records=500
        (Upload CSV file with Content-Type: multipart/form-data)
    """
    logger.info(f"Processing CSV upload: {file.filename}")

    try:
        content = await file.read()
        df = add_postcode_column_pandas(content)

        # Limit records returned
        limited_data = df.head(min(records, 10000))

        # Log first few rows
        logger.info(f"First 5 rows of processed data:\n{df.iloc[:5, :8].to_string(index=False)}")

        result = limited_data.to_dict(orient='records')

        return {
            "column_names": df.columns.tolist(),
            "data": result,
            "records_returned": len(result),
            "total_records": len(df)
        }

    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"CSV processing error: {str(e)}")


# ===== CSV Processing Helper Functions =====

def add_postcode_column_pandas(input_file: bytes, missing_value: str = 'UNKNOWN') -> pd.DataFrame:
    """
    Add a postcode column to CSV data by extracting from all columns.

    Args:
        input_file: CSV file content as bytes
        missing_value: Value to use when no postcode found (default: 'UNKNOWN')

    Returns:
        DataFrame with 'postcode' as the first column
    """
    logger.info("Processing CSV to add postcode column")

    try:
        # Load CSV from bytes
        df = pd.read_csv(io.BytesIO(input_file))
        logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")

        # Create full address string by concatenating all columns
        df['full_address'] = df.astype(str).agg(' '.join, axis=1)

        # Extract postcode using flexible function
        df['postcode'] = df['full_address'].apply(
            lambda x: extract_uk_postcode_from_string_flexible(x) or missing_value
        )

        # Move 'postcode' to the front
        cols = ['postcode'] + [col for col in df.columns if col not in ['postcode', 'full_address']]
        df = df[cols]

        # Handle NaN and bad values
        df = handle_nan_and_bad_values(df)

        logger.info(f"Successfully processed CSV with {len(df)} records")
        return df

    except Exception as e:
        logger.error(f"Error in add_postcode_column_pandas: {str(e)}", exc_info=True)
        raise


def handle_nan_and_bad_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DataFrame by handling NaN, infinity, and bad values.

    Args:
        df: DataFrame to clean

    Returns:
        Cleaned DataFrame
    """
    try:
        # Identify column types
        numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()

        # Handle numeric columns: replace inf/-inf with None, then fill NaN with 0
        df[numeric_cols] = df[numeric_cols].replace({float('inf'): None, float('-inf'): None}).fillna(0)

        # Handle text columns: replace NaN with empty string
        df[text_cols] = df[text_cols].fillna('')

        # Handle monetary columns (strip currency symbols and convert)
        monetary_cols = [col for col in df.columns if any(word in col.lower() for word in ['rate', 'cost', 'price', 'salary', 'fee'])]
        for col in monetary_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[£$,]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df

    except Exception as e:
        logger.error(f"Error in handle_nan_and_bad_values: {str(e)}", exc_info=True)
        raise


# ===== Health Check =====

@router.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "service": "location-service",
        "endpoints": [
            "GET /api/postcodes/{postcode}",
            "POST /api/postcodes/batch",
            "GET /api/postcodes/search/{pattern}",
            "POST /api/postcodes/upload/csv"
        ]
    }
