"""
Resource discovery and loading for Staff Specialisations.

This module provides ResourceLoader for discovering, loading, and caching
role-specific resources from the file system.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
import re

from .models import Resource, ResourceFormat, ResourceMetadata


logger = logging.getLogger(__name__)


class ResourceLoader:
    """Discovers and loads resources from staff role directories."""

    def __init__(self, base_path: Path, cache_ttl_seconds: int = 3600):
        """
        Initialize ResourceLoader.

        Args:
            base_path: Base path to Staff Specialisation Resources directory
            cache_ttl_seconds: Cache time-to-live in seconds (default 1 hour)
        """
        self.base_path = Path(base_path)
        self.cache_ttl_seconds = cache_ttl_seconds
        self._resource_cache: Dict[str, Dict[str, Resource]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._guide_cache: Dict[str, Optional[str]] = {}
        self._guide_timestamps: Dict[str, float] = {}

    def discover_resources(self, role_dir: Path) -> Dict[str, Path]:
        """
        Discover all resources in a role directory (excluding resources-guide.md).

        Args:
            role_dir: Path to role directory

        Returns:
            Dict mapping resource names to their paths, sorted alphabetically

        Example:
            ```python
            resources = loader.discover_resources(Path("Staff Specialisation Resources/person_1"))
            # Returns: {"guide": Path(...), "decision_framework": Path(...), ...}
            ```
        """
        if not role_dir.exists():
            logger.info(f"Role directory does not exist: {role_dir}")
            return {}

        if not role_dir.is_dir():
            logger.warning(f"Role path is not a directory: {role_dir}")
            return {}

        resources = {}
        try:
            for file_path in sorted(role_dir.iterdir()):
                if not file_path.is_file():
                    continue

                # Skip resources-guide.md
                if file_path.name == "resources-guide.md":
                    continue

                # Get resource name (filename without extension)
                name = file_path.stem
                resources[name] = file_path

            logger.debug(f"Discovered {len(resources)} resources in {role_dir}")
            return resources

        except (OSError, PermissionError) as e:
            logger.error(f"Error discovering resources in {role_dir}: {e}")
            return {}

    def load_guide(self, role_dir: Path) -> Optional[str]:
        """
        Load resources-guide.md from a role directory.

        Args:
            role_dir: Path to role directory

        Returns:
            Content of resources-guide.md if it exists, None otherwise

        Example:
            ```python
            guide = loader.load_guide(Path("Staff Specialisation Resources/person_1"))
            if guide:
                print(guide)  # # Resource Guide...
            ```
        """
        guide_path = role_dir / "resources-guide.md"

        if not guide_path.exists():
            logger.debug(f"No resources guide found in {role_dir}")
            return None

        try:
            with open(guide_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Loaded resources guide from {guide_path}")
            return content

        except (OSError, IOError, UnicodeDecodeError) as e:
            logger.error(f"Error loading resources guide from {guide_path}: {e}")
            return None

    def load_resource(self, resource_path: Path) -> Resource:
        """
        Load and parse a single resource file.

        Detects file format and parses accordingly (markdown, JSON, text).

        Args:
            resource_path: Path to resource file

        Returns:
            Resource object with parsed content

        Example:
            ```python
            resource = loader.load_resource(Path("resources/guide.md"))
            print(resource.parsed)  # {"format": "markdown", "content": "...", ...}
            ```
        """
        # Create metadata
        try:
            stat = resource_path.stat()
            metadata = ResourceMetadata(
                name=resource_path.stem,
                path=resource_path,
                format=self._detect_format(resource_path),
                size_bytes=stat.st_size,
                is_guide=False,
                created_at=stat.st_ctime,
                updated_at=stat.st_mtime,
            )
        except OSError as e:
            logger.error(f"Error creating metadata for {resource_path}: {e}")
            return Resource(
                metadata=None,
                content="",
                parsed={},
                error=f"Failed to read file metadata: {e}",
            )

        # Read content
        try:
            with open(resource_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, IOError, UnicodeDecodeError) as e:
            logger.error(f"Error reading resource file {resource_path}: {e}")
            return Resource(
                metadata=metadata,
                content="",
                parsed={},
                error=f"Failed to read file content: {e}",
            )

        # Parse content
        parsed = self._parse_resource(content, metadata.format)
        error = None if parsed else f"Failed to parse {metadata.format} content"

        if error:
            logger.warning(f"Error parsing {resource_path}: {error}")

        resource = Resource(
            metadata=metadata,
            content=content,
            parsed=parsed or {},
            error=error,
        )

        logger.debug(f"Loaded resource {resource_path} ({metadata.format})")
        return resource

    def load_resources(
        self, role_name: str, force_refresh: bool = False
    ) -> Dict[str, Resource]:
        """
        Load all resources for a role (with caching).

        Args:
            role_name: Role name (e.g., "person_1_managing_director")
            force_refresh: Force reload from disk, bypass cache

        Returns:
            Dict mapping resource names to Resource objects

        Example:
            ```python
            resources = loader.load_resources("person_1_managing_director")
            # Returns: {"guide": Resource(...), "framework": Resource(...), ...}
            ```
        """
        # Check cache
        if not force_refresh:
            if role_name in self._resource_cache:
                if self._is_cache_valid(role_name):
                    logger.debug(f"Returning cached resources for {role_name}")
                    return self._resource_cache[role_name]

        # Load from disk
        role_dir = self.base_path / role_name
        discovered = self.discover_resources(role_dir)
        resources = {}

        for resource_name, resource_path in discovered.items():
            resources[resource_name] = self.load_resource(resource_path)

        # Cache results
        self._resource_cache[role_name] = resources
        self._cache_timestamps[role_name] = time.time()

        logger.debug(f"Loaded and cached {len(resources)} resources for {role_name}")
        return resources

    def invalidate_cache(self, role_name: Optional[str] = None):
        """
        Invalidate cache for a role (or all roles if None).

        Args:
            role_name: Role name to invalidate, or None for all

        Example:
            ```python
            loader.invalidate_cache("person_1_managing_director")
            loader.invalidate_cache()  # Clear all
            ```
        """
        if role_name is None:
            self._resource_cache.clear()
            self._cache_timestamps.clear()
            self._guide_cache.clear()
            self._guide_timestamps.clear()
            logger.debug("Invalidated all caches")
        else:
            self._resource_cache.pop(role_name, None)
            self._cache_timestamps.pop(role_name, None)
            self._guide_cache.pop(role_name, None)
            self._guide_timestamps.pop(role_name, None)
            logger.debug(f"Invalidated cache for {role_name}")

    # Private helper methods

    def _detect_format(self, resource_path: Path) -> ResourceFormat:
        """Detect resource format from file extension."""
        suffix = resource_path.suffix.lower()
        if suffix == ".md":
            return ResourceFormat.MARKDOWN
        elif suffix == ".json":
            return ResourceFormat.JSON
        else:
            return ResourceFormat.TEXT

    def _parse_resource(
        self, content: str, format: ResourceFormat
    ) -> Optional[Dict]:
        """Parse resource content based on format."""
        try:
            if format == ResourceFormat.MARKDOWN:
                return self._parse_markdown(content)
            elif format == ResourceFormat.JSON:
                return self._parse_json(content)
            else:  # TEXT
                return self._parse_text(content)
        except Exception as e:
            logger.error(f"Error parsing {format.value} content: {e}")
            return None

    def _parse_markdown(self, content: str) -> Dict:
        """Parse markdown content."""
        # Extract headings
        headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)

        return {
            "format": ResourceFormat.MARKDOWN.value,
            "content": content,
            "headings": headings,
        }

    def _parse_json(self, content: str) -> Dict:
        """Parse JSON content."""
        data = json.loads(content)
        return {
            "format": ResourceFormat.JSON.value,
            "data": data,
        }

    def _parse_text(self, content: str) -> Dict:
        """Parse plain text content."""
        lines = content.split("\n")
        return {
            "format": ResourceFormat.TEXT.value,
            "content": content,
            "lines": lines,
        }

    def _is_cache_valid(self, role_name: str) -> bool:
        """Check if cache entry is still valid."""
        if role_name not in self._cache_timestamps:
            return False

        age_seconds = time.time() - self._cache_timestamps[role_name]
        return age_seconds < self.cache_ttl_seconds


__all__ = ["ResourceLoader"]
