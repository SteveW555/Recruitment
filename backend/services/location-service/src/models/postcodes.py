"""
SQLAlchemy models for UK postcode and demographics data.

This module defines database tables for storing UK postcode information
including coordinates, administrative areas, and demographic statistics.
"""

from sqlalchemy import Column, Integer, String, Float, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from ..db.database import Base


class Postcodes(Base):
    """
    UK Postcodes table with geographic coordinates and administrative areas.

    Stores detailed information about UK postcodes including latitude/longitude,
    town, and county information for geolocation services.

    Attributes:
        id: Primary key
        postcode: UK postcode (e.g., "BS1 4DJ")
        lat: Latitude coordinate (WGS84)
        lng: Longitude coordinate (WGS84)
        town: Town or city name
        county: County name
    """
    __tablename__ = "postcodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    postcode = Column(String(10), unique=True, index=True, nullable=False,
                     comment="UK postcode in format 'XX## #XX'")
    lat = Column(Float, nullable=False, comment="Latitude coordinate (WGS84)")
    lng = Column(Float, nullable=False, comment="Longitude coordinate (WGS84)")
    town = Column(String(100), index=True, comment="Town or city name")
    county = Column(String(100), index=True, comment="County name")

    # Additional indexes for common queries
    __table_args__ = (
        Index('idx_postcode_town', 'town'),
        Index('idx_postcode_county', 'county'),
        Index('idx_postcode_coordinates', 'lat', 'lng'),
    )

    def __repr__(self):
        return f"<Postcode(postcode='{self.postcode}', town='{self.town}', county='{self.county}')>"

    def to_dict(self):
        """
        Convert model instance to dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of postcode data
        """
        return {
            'id': self.id,
            'postcode': self.postcode,
            'lat': float(self.lat),
            'lng': float(self.lng),
            'town': self.town,
            'county': self.county
        }


class Demographics(Base):
    """
    UK Demographics data by postcode sector.

    Stores socioeconomic and demographic statistics for UK postcode sectors.
    Used for candidate and client profiling, market analysis, and targeting.

    Attributes:
        id: Primary key
        postcode_sector: Postcode sector (e.g., "BS1 4")
        population: Total population
        social_grade_ab: Percentage of AB social grade (Higher/Intermediate managerial)
        social_grade_c1: Percentage of C1 social grade (Supervisory/clerical)
        social_grade_c2: Percentage of C2 social grade (Skilled manual)
        social_grade_de: Percentage of DE social grade (Semi-skilled/unskilled)
        median_income: Median household income
        employment_rate: Employment rate as percentage
        data_source: Source of demographic data
    """
    __tablename__ = "demographics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    postcode_sector = Column(String(10), unique=True, index=True, nullable=False,
                            comment="Postcode sector (e.g., 'BS1 4')")
    population = Column(Integer, comment="Total population in sector")
    social_grade_ab = Column(Float, comment="% AB social grade (Higher/Intermediate managerial)")
    social_grade_c1 = Column(Float, comment="% C1 social grade (Supervisory/clerical)")
    social_grade_c2 = Column(Float, comment="% C2 social grade (Skilled manual)")
    social_grade_de = Column(Float, comment="% DE social grade (Semi-skilled/unskilled)")
    median_income = Column(Float, comment="Median household income (GBP)")
    employment_rate = Column(Float, comment="Employment rate as percentage")
    data_source = Column(String(100), comment="Source of demographic data")

    # Index for common queries
    __table_args__ = (
        Index('idx_demographics_sector', 'postcode_sector'),
    )

    def __repr__(self):
        return f"<Demographics(sector='{self.postcode_sector}', population={self.population})>"

    def to_dict(self):
        """
        Convert model instance to dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of demographics data
        """
        return {
            'id': self.id,
            'postcode_sector': self.postcode_sector,
            'population': self.population,
            'social_grade_ab': float(self.social_grade_ab) if self.social_grade_ab else None,
            'social_grade_c1': float(self.social_grade_c1) if self.social_grade_c1 else None,
            'social_grade_c2': float(self.social_grade_c2) if self.social_grade_c2 else None,
            'social_grade_de': float(self.social_grade_de) if self.social_grade_de else None,
            'median_income': float(self.median_income) if self.median_income else None,
            'employment_rate': float(self.employment_rate) if self.employment_rate else None,
            'data_source': self.data_source
        }
