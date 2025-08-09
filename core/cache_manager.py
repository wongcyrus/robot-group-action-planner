"""
File-based cache manager for Robot Action Planner.
Handles persistent caching of spreadsheet data to improve startup performance.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from constant import (
    ALWAYS_SAVE_CACHE,
    CACHE_DIRECTORY,
    CACHE_EXPIRY_HOURS,
    USE_FILE_CACHE,
)


class FileCacheManager:
    """Manages persistent file-based caching for spreadsheet data."""

    def __init__(self):
        """Initialize the cache manager."""
        self.logger = logging.getLogger("FileCacheManager")
        # Use project root directory instead of core directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.cache_dir = os.path.join(project_root, CACHE_DIRECTORY)
        self.load_enabled = USE_FILE_CACHE  # Controls whether to load from cache
        self.save_enabled = (
            USE_FILE_CACHE or ALWAYS_SAVE_CACHE
        )  # Controls whether to save cache
        self.expiry_hours = CACHE_EXPIRY_HOURS

        # Always ensure cache directory exists if we need to save
        if self.save_enabled:
            self._ensure_cache_directory()

        if self.load_enabled:
            self.logger.info(f"File cache loading enabled. Directory: {self.cache_dir}")
        else:
            self.logger.info("File cache loading disabled")

        if self.save_enabled and not self.load_enabled:
            self.logger.info(
                f"Cache saving enabled for debugging. Directory: {self.cache_dir}"
            )
        elif not self.save_enabled:
            self.logger.info("Cache saving disabled")

        self.logger.info(f"Cache expiry: {self.expiry_hours} hours")

    def _ensure_cache_directory(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create cache directory: {e}")
            self.save_enabled = False

    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get the full path for a cache file."""
        # Create a safe filename from the cache key
        safe_key = hashlib.md5(cache_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def _get_cache_key_file_path(self, cache_key: str) -> str:
        """Get the full path for a cache file using the original cache key as filename."""
        # Create a safe filename from the cache key by replacing invalid characters
        safe_cache_key = "".join(
            c for c in cache_key if c.isalnum() or c in "._-"
        ).rstrip()
        # Truncate if too long (Windows has 255 char limit)
        if len(safe_cache_key) > 200:
            safe_cache_key = safe_cache_key[:200]
        return os.path.join(self.cache_dir, f"{safe_cache_key}.json")

    def _is_cache_valid(self, cache_file_path: str) -> bool:
        """Check if cache file exists and is not expired."""
        if not os.path.exists(cache_file_path):
            return False

        if self.expiry_hours <= 0:  # Never expire
            return True

        try:
            # Check file modification time
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file_path))
            expiry_time = file_time + timedelta(hours=self.expiry_hours)
            return datetime.now() < expiry_time
        except Exception as e:
            self.logger.warning(f"Error checking cache validity: {e}")
            return False

    def get_cache(self, cache_key: str) -> Optional[Any]:
        """
        Retrieve data from cache.

        Args:
            cache_key: Unique identifier for the cached data

        Returns:
            Cached data if found and valid, None otherwise
        """
        if not self.load_enabled:
            return None

        try:
            cache_file_path = self._get_cache_file_path(cache_key)

            if not self._is_cache_valid(cache_file_path):
                self.logger.debug(f"Cache miss or expired for key: {cache_key}")
                return None

            with open(cache_file_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Verify cache structure
            if not isinstance(cache_data, dict) or "data" not in cache_data:
                self.logger.warning(f"Invalid cache structure for key: {cache_key}")
                return None

            self.logger.debug(f"Cache hit for key: {cache_key}")
            return cache_data["data"]

        except Exception as e:
            self.logger.warning(f"Error reading cache for key {cache_key}: {e}")
            return None

    def set_cache(self, cache_key: str, data: Any) -> bool:
        """
        Store data in cache.

        Args:
            cache_key: Unique identifier for the cached data
            data: Data to cache

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.save_enabled:
            return False

        try:
            cache_file_path = self._get_cache_file_path(cache_key)
            cache_key_file_path = self._get_cache_key_file_path(cache_key)

            cache_data = {
                "cache_key": cache_key,
                "timestamp": time.time(),
                "data": data,
            }

            # Save with MD5 hash filename (primary)
            with open(cache_file_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            # Save copy with cache key filename (for human readability)
            try:
                with open(cache_key_file_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                # If cache key filename fails, continue with just the MD5 version
                self.logger.debug(f"Could not save cache key filename copy: {e}")

            self.logger.debug(f"Data cached for key: {cache_key}")
            return True

        except Exception as e:
            self.logger.warning(f"Error writing cache for key {cache_key}: {e}")
            return False

    def clear_cache(self, cache_key: Optional[str] = None) -> bool:
        """
        Clear cache data.

        Args:
            cache_key: Specific cache key to clear. If None, clears all cache.

        Returns:
            True if successfully cleared, False otherwise
        """
        if not self.save_enabled:
            return False

        try:
            if cache_key:
                # Clear specific cache (both MD5 and cache key versions)
                cache_file_path = self._get_cache_file_path(cache_key)
                cache_key_file_path = self._get_cache_key_file_path(cache_key)

                files_removed = 0
                if os.path.exists(cache_file_path):
                    os.remove(cache_file_path)
                    files_removed += 1

                if os.path.exists(cache_key_file_path):
                    os.remove(cache_key_file_path)
                    files_removed += 1

                if files_removed > 0:
                    self.logger.info(
                        f"Cache cleared for key: {cache_key} ({files_removed} files removed)"
                    )
                return True
            else:
                # Clear all cache files
                if os.path.exists(self.cache_dir):
                    for filename in os.listdir(self.cache_dir):
                        if filename.endswith(".json"):
                            file_path = os.path.join(self.cache_dir, filename)
                            os.remove(file_path)
                    self.logger.info("All cache files cleared")
                return True

        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the cache.

        Returns:
            Dictionary with cache statistics and information
        """
        info = {
            "load_enabled": self.load_enabled,
            "save_enabled": self.save_enabled,
            "cache_directory": self.cache_dir,
            "expiry_hours": self.expiry_hours,
            "total_files": 0,
            "total_size_bytes": 0,
            "files": [],
        }

        if not self.save_enabled or not os.path.exists(self.cache_dir):
            return info

        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_stat = os.stat(file_path)

                    info["total_files"] += 1
                    info["total_size_bytes"] += file_stat.st_size

                    # Try to read cache metadata
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            cache_data = json.load(f)

                        file_info = {
                            "filename": filename,
                            "size_bytes": file_stat.st_size,
                            "modified": datetime.fromtimestamp(
                                file_stat.st_mtime
                            ).isoformat(),
                            "cache_key": cache_data.get("cache_key", "unknown"),
                            "valid": self._is_cache_valid(file_path),
                        }
                        info["files"].append(file_info)
                    except:
                        # Skip files that can't be read
                        pass

        except Exception as e:
            self.logger.error(f"Error getting cache info: {e}")

        return info

    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache files.

        Returns:
            Number of files removed
        """
        if not self.save_enabled or self.expiry_hours <= 0:
            return 0

        removed_count = 0
        try:
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith(".json"):
                        file_path = os.path.join(self.cache_dir, filename)
                        if not self._is_cache_valid(file_path):
                            os.remove(file_path)
                            removed_count += 1
                            self.logger.debug(f"Removed expired cache file: {filename}")

            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} expired cache files")

        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")

        return removed_count


# Global cache manager instance
cache_manager = FileCacheManager()
