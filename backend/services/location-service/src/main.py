"""
Location Service - FastAPI Application

UK Postcode and Geography microservice for ProActive People recruitment platform.
Provides REST API endpoints for postcode lookups, geographic data, and CSV processing.

Author: ProActive People Ltd
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .db import init_db, check_connection
from .routes import router as postcodes_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle (startup and shutdown).

    Startup:
        - Check database connection
        - Initialize database tables
        - Log service information

    Shutdown:
        - Clean up resources
        - Log shutdown information
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Location Service Starting Up")
    logger.info("=" * 60)

    # Check database connection
    if check_connection():
        logger.info("✓ Database connection successful")
        # Initialize database tables
        try:
            init_db()
            logger.info("✓ Database tables initialized")
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {str(e)}")
    else:
        logger.error("✗ Database connection failed")
        logger.warning("Service will start but database operations will fail")

    logger.info(f"✓ Service ready on port {os.getenv('LOCATION_SERVICE_PORT', '8001')}")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Location Service Shutting Down")


# Create FastAPI application
app = FastAPI(
    title="Location Service API",
    description="UK Postcode and Geography microservice for recruitment platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(postcodes_router)


# Root endpoint
@app.get("/")
async def root():
    """Service information endpoint."""
    return {
        "service": "Location Service",
        "version": "1.0.0",
        "status": "running",
        "description": "UK Postcode and Geography API",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/postcodes/health"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Service health check endpoint.

    Returns service status and database connectivity.
    """
    db_status = check_connection()

    return {
        "status": "healthy" if db_status else "degraded",
        "service": "location-service",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }


def main():
    """Entry point for command-line execution."""
    import uvicorn

    port = int(os.getenv("LOCATION_SERVICE_PORT", "8001"))
    host = os.getenv("LOCATION_SERVICE_HOST", "0.0.0.0")

    logger.info(f"Starting Location Service on {host}:{port}")

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=os.getenv("NODE_ENV") == "development",
        log_level="info"
    )


if __name__ == "__main__":
    main()
