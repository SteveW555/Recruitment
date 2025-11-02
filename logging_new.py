"""
Unified Logging System for ProActive People Recruitment System

Provides consistent logging across Python backend and JavaScript frontend.
Logs to both terminal (with colors) and files.

Usage:
    from logging_new import Logger

    logger = Logger(service_name="backend-api")
    logger.info("Server started")
    logger.error("Connection failed", {"host": "localhost", "port": 5432})
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import json


class ColorCodes:
    """ANSI color codes for terminal output"""

    # Service colors
    FRONTEND = '\033[94m'      # Blue
    BACKEND = '\033[92m'       # Green
    PYTHON = '\033[93m'        # Yellow
    ROUTER = '\033[95m'        # Magenta
    DEFAULT = '\033[96m'       # Cyan

    # Log level colors
    DEBUG = '\033[37m'         # White
    INFO = '\033[97m'          # Bright White
    WARNING = '\033[93m'       # Yellow
    ERROR = '\033[91m'         # Red
    CRITICAL = '\033[95m\033[1m'  # Magenta Bold

    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'


class LogFormatter(logging.Formatter):
    """Custom formatter with colors and consistent format"""

    def __init__(self, service_name: str, use_colors: bool = True):
        super().__init__()
        self.service_name = service_name
        self.use_colors = use_colors

        # Map service names to colors
        self.service_colors = {
            'frontend': ColorCodes.FRONTEND,
            'backend': ColorCodes.BACKEND,
            'backend-api': ColorCodes.BACKEND,
            'python': ColorCodes.PYTHON,
            'router': ColorCodes.ROUTER,
            'ai-router': ColorCodes.ROUTER,
        }

        # Map log levels to colors
        self.level_colors = {
            'DEBUG': ColorCodes.DEBUG,
            'INFO': ColorCodes.INFO,
            'WARNING': ColorCodes.WARNING,
            'ERROR': ColorCodes.ERROR,
            'CRITICAL': ColorCodes.CRITICAL,
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and consistent structure"""

        # Get timestamp (time only, no date)
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')

        # Get service color
        service_lower = self.service_name.lower()
        service_color = self.service_colors.get(
            service_lower,
            ColorCodes.DEFAULT
        )

        # Get level color
        level_color = self.level_colors.get(record.levelname, ColorCodes.INFO)

        # Format the message
        message = record.getMessage()

        # Add extra data if present
        if hasattr(record, 'extra_data') and record.extra_data:
            try:
                extra_json = json.dumps(record.extra_data, indent=2)
                message = f"{message}\n{extra_json}"
            except Exception:
                message = f"{message}\n{record.extra_data}"

        if self.use_colors:
            # Colored format for terminal
            return (
                f"{ColorCodes.BOLD}[{timestamp}]{ColorCodes.RESET} "
                f"{service_color}[{self.service_name.upper()}]{ColorCodes.RESET} "
                f"{level_color}[{record.levelname}]{ColorCodes.RESET} "
                f"{message}"
            )
        else:
            # Plain format for files
            return (
                f"[{timestamp}] "
                f"[{self.service_name.upper()}] "
                f"[{record.levelname}] "
                f"{message}"
            )


class Logger:
    """Unified logger that writes to both terminal and files"""

    def __init__(self, service_name: str = "backend", log_dir: str = "logs"):
        """
        Initialize logger

        Args:
            service_name: Name of the service (frontend, backend, python, router, etc.)
            log_dir: Directory to store log files
        """
        self.service_name = service_name
        self.log_dir = Path(log_dir)

        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)

        # Create logger instance
        self.logger = logging.getLogger(f"unified_{service_name}")
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Console handler (with colors)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(LogFormatter(service_name, use_colors=True))
        self.logger.addHandler(console_handler)

        # File handler - combined log (no colors)
        combined_log = self.log_dir / "combined.log"
        file_handler = logging.FileHandler(combined_log, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LogFormatter(service_name, use_colors=False))
        self.logger.addHandler(file_handler)

        # File handler - service-specific log (no colors)
        service_log = self.log_dir / f"{service_name}.log"
        service_handler = logging.FileHandler(service_log, encoding='utf-8')
        service_handler.setLevel(logging.DEBUG)
        service_handler.setFormatter(LogFormatter(service_name, use_colors=False))
        self.logger.addHandler(service_handler)

        # File handler - error log only (no colors)
        error_log = self.log_dir / "errors.log"
        error_handler = logging.FileHandler(error_log, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(LogFormatter(service_name, use_colors=False))
        self.logger.addHandler(error_handler)

    def _log(self, level: int, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        if extra_data:
            # Create a custom LogRecord with extra data
            record = self.logger.makeRecord(
                self.logger.name,
                level,
                "(unknown file)",
                0,
                message,
                (),
                None
            )
            record.extra_data = extra_data
            self.logger.handle(record)
        else:
            self.logger.log(level, message)

    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log(logging.DEBUG, message, extra_data)

    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log(logging.INFO, message, extra_data)

    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log(logging.WARNING, message, extra_data)

    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._log(logging.ERROR, message, extra_data)

    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self._log(logging.CRITICAL, message, extra_data)

    # Convenience aliases
    def warn(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Alias for warning"""
        self.warning(message, extra_data)


# Singleton instances for common services
frontend_logger = Logger("frontend")
backend_logger = Logger("backend-api")
router_logger = Logger("ai-router")
python_logger = Logger("python")


# Test function
def test_logger():
    """Test the logging system with various services and levels"""
    print("\n=== Testing Unified Logging System ===\n")

    # Test different services
    services = [
        ("frontend", "Frontend application started"),
        ("backend-api", "Backend API server listening on port 3002"),
        ("ai-router", "AI Router initialized successfully"),
        ("python", "Python service ready"),
    ]

    for service_name, message in services:
        logger = Logger(service_name)
        logger.info(message)

    print()

    # Test different log levels
    test_logger = Logger("test-service")
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")

    print()

    # Test with extra data
    test_logger.info("Database connection established", {
        "host": "localhost",
        "port": 5432,
        "database": "recruitment"
    })

    test_logger.error("API request failed", {
        "endpoint": "/api/candidates",
        "status_code": 500,
        "error": "Internal server error"
    })

    print("\n=== Log files created in logs/ directory ===")
    print("  - logs/combined.log (all services)")
    print("  - logs/errors.log (errors only)")
    print("  - logs/<service-name>.log (per service)")
    print()


if __name__ == "__main__":
    test_logger()
