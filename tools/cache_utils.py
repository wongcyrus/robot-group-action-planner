#!/usr/bin/env python3
"""
Cache Management Utility for Robot Action Planner
Provides tools to manage the file-based cache system.
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add the current directory to Python path
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

from core.cache_manager import cache_manager
from core.spreadsheet_loader import SpreadsheetLoader


def show_cache_info():
    """Display detailed cache information."""
    print("=" * 60)
    print("CACHE INFORMATION")
    print("=" * 60)

    info = cache_manager.get_cache_info()

    print(f"Cache Status: {'Enabled' if info['enabled'] else 'Disabled'}")
    print(f"Cache Directory: {info['cache_directory']}")
    print(
        f"Expiry Hours: {info['expiry_hours']} ({'Never' if info['expiry_hours'] <= 0 else 'hours'})"
    )
    print(f"Total Files: {info['total_files']}")
    print(
        f"Total Size: {info['total_size_bytes']} bytes ({info['total_size_bytes'] / 1024:.1f} KB)"
    )

    if info["files"]:
        print("\nCache Files:")
        print("-" * 60)
        for file_info in info["files"]:
            status = "✓ Valid" if file_info["valid"] else "✗ Expired"
            print(f"Key: {file_info['cache_key']}")
            print(f"File: {file_info['filename']}")
            print(f"Size: {file_info['size_bytes']} bytes")
            print(f"Modified: {file_info['modified']}")
            print(f"Status: {status}")
            print("-" * 60)
    else:
        print("\nNo cache files found.")


def clear_cache(cache_key=None):
    """Clear cache files."""
    if cache_key:
        success = cache_manager.clear_cache(cache_key)
        if success:
            print(f"✓ Cache cleared for key: {cache_key}")
        else:
            print(f"✗ Failed to clear cache for key: {cache_key}")
    else:
        success = cache_manager.clear_cache()
        if success:
            print("✓ All cache files cleared")
        else:
            print("✗ Failed to clear cache files")


def clear_memory_cache():
    """Clear in-memory caches."""
    SpreadsheetLoader.clear_all_caches()
    print("✓ In-memory caches cleared")


def cleanup_expired():
    """Remove expired cache files."""
    removed_count = cache_manager.cleanup_expired_cache()
    if removed_count > 0:
        print(f"✓ Removed {removed_count} expired cache files")
    else:
        print("No expired cache files found")


def test_cache_performance():
    """Test cache performance by loading a sample song."""
    print("=" * 60)
    print("CACHE PERFORMANCE TEST")
    print("=" * 60)

    import time

    # Use a sample song name (modify if needed)
    test_song = "06-90"

    print(f"Testing with song: {test_song}")

    # Clear cache first
    cache_manager.clear_cache()
    SpreadsheetLoader.clear_all_caches()
    print("Cache cleared for test")

    # First load (no cache)
    print("\n1. First load (no cache)...")
    start_time = time.time()
    try:
        loader = SpreadsheetLoader(test_song)
        actions = loader.get_robot_actions()
        details = loader.get_action_details()
        first_load_time = time.time() - start_time
        print(
            f"   ✓ Loaded {len(actions)} robot actions and {len(details)} action details"
        )
        print(f"   Time: {first_load_time:.2f} seconds")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return

    # Second load (with cache)
    print("\n2. Second load (with cache)...")
    start_time = time.time()
    try:
        loader = SpreadsheetLoader(test_song)
        actions = loader.get_robot_actions()
        details = loader.get_action_details()
        second_load_time = time.time() - start_time
        print(
            f"   ✓ Loaded {len(actions)} robot actions and {len(details)} action details"
        )
        print(f"   Time: {second_load_time:.2f} seconds")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return

    # Show improvement
    if first_load_time > 0:
        improvement = ((first_load_time - second_load_time) / first_load_time) * 100
        speedup = (
            first_load_time / second_load_time if second_load_time > 0 else float("inf")
        )
        print(f"\n📊 PERFORMANCE RESULTS:")
        print(f"   Time saved: {first_load_time - second_load_time:.2f} seconds")
        print(f"   Improvement: {improvement:.1f}%")
        print(f"   Speedup: {speedup:.1f}x faster")


def validate_cache():
    """Validate cache files for corruption."""
    print("=" * 60)
    print("CACHE VALIDATION")
    print("=" * 60)

    info = cache_manager.get_cache_info()

    if not info["enabled"]:
        print("Cache is disabled")
        return

    if not info["files"]:
        print("No cache files to validate")
        return

    valid_count = 0
    invalid_count = 0

    for file_info in info["files"]:
        if file_info["valid"]:
            print(f"✓ {file_info['cache_key']}")
            valid_count += 1
        else:
            print(f"✗ {file_info['cache_key']} (expired)")
            invalid_count += 1

    print(f"\nValidation Results:")
    print(f"Valid files: {valid_count}")
    print(f"Expired files: {invalid_count}")


def main():
    """Main entry point for cache management utility."""
    parser = argparse.ArgumentParser(
        description="Robot Action Planner Cache Management"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Show cache information")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear cache")
    clear_parser.add_argument("--key", help="Specific cache key to clear")
    clear_parser.add_argument(
        "--memory", action="store_true", help="Clear in-memory cache only"
    )

    # Cleanup command
    subparsers.add_parser("cleanup", help="Remove expired cache files")

    # Test command
    subparsers.add_parser("test", help="Test cache performance")

    # Validate command
    subparsers.add_parser("validate", help="Validate cache files")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "info":
            show_cache_info()
        elif args.command == "clear":
            if args.memory:
                clear_memory_cache()
            else:
                clear_cache(args.key)
        elif args.command == "cleanup":
            cleanup_expired()
        elif args.command == "test":
            test_cache_performance()
        elif args.command == "validate":
            validate_cache()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
