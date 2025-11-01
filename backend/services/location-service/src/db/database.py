"""
Database configuration and session management for location-service.

Handles PostgreSQL connection pooling and session lifecycle for all
location-related database operations.
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database connection configuration from environment
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_this_password_in_production")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "recruitment")

# Construct database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("POSTGRES_POOL_MIN", "2")),
    max_overflow=int(os.getenv("POSTGRES_POOL_MAX", "10")) - int(os.getenv("POSTGRES_POOL_MIN", "2")),
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("NODE_ENV") == "development",  # Log SQL in dev mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.

    Yields a database session and ensures it's properly closed after use.
    Use this with FastAPI's Depends() to inject database sessions into endpoints.

    Example:
        @router.get("/postcodes/{postcode}")
        def get_postcode(postcode: str, db: Session = Depends(get_db)):
            return db.query(Postcodes).filter(Postcodes.postcode == postcode).first()

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.

    Creates all tables defined in models if they don't exist.
    Should be called on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def check_connection():
    """
    Check database connectivity.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
