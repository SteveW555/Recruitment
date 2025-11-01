"""
Location Service Package Setup
ProActive People - UK Postcode & Geography API
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="location-service",
    version="1.0.0",
    description="UK Postcode and Geography microservice for recruitment platform",
    author="ProActive People Ltd",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'location-service=src.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
