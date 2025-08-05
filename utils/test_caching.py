#!/usr/bin/env python3
"""
Test script to demonstrate the caching functionality of the Robot Action Planner.
This script shows the performance improvement from caching spreadsheet data.
"""

import os
import sys
import time
import logging

# Add the parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

from spreadsheet_loader import SpreadsheetLoader
from action_compiler import ActionCompiler
from cache_manager import cache_manager


def test_caching_performance():
    """Test the performance improvement from caching."""
    print("=" * 60)
    print("TESTING FILE-BASED CACHING PERFORMANCE")
    print("=" * 60)
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Show cache configuration
    cache_info = cache_manager.get_cache_info()
    print(f"File cache enabled: {cache_info['enabled']}")
    print(f"Cache directory: {cache_info['cache_directory']}")
    print(f"Cache expiry: {cache_info['expiry_hours']} hours")
    
    # Simulate song names (you can modify these based on your actual songs)
    test_songs = ["06-90", "test-song", "another-song"]
    
    print(f"\nTesting with songs: {test_songs}")
    
    # Clear all caches first for accurate testing
    print("\n--- CLEARING ALL CACHES ---")
    cache_manager.clear_cache()  # Clear file cache
    SpreadsheetLoader.clear_all_caches()  # Clear memory cache
    print("All caches cleared")
    
    # Test 1: First load (no cache)
    print("\n--- FIRST LOAD (No Cache) ---")
    start_time = time.time()
    
    first_load_results = {}
    for song in test_songs:
        song_start = time.time()
        print(f"Loading {song}...")
        try:
            loader = SpreadsheetLoader(song)
            compiler = ActionCompiler(loader)
            actions = compiler.compile_actions()
            song_time = time.time() - song_start
            first_load_results[song] = {
                'success': True,
                'actions': len(actions),
                'time': song_time
            }
            print(f"  ✓ {song}: {len(actions)} actions loaded in {song_time:.2f}s")
        except Exception as e:
            song_time = time.time() - song_start
            first_load_results[song] = {
                'success': False,
                'actions': 0,
                'time': song_time
            }
            print(f"  ✗ {song}: Failed to load in {song_time:.2f}s - {e}")
    
    first_load_time = time.time() - start_time
    print(f"Total first load time: {first_load_time:.2f} seconds")
    
    # Show what's in cache now
    cache_info = cache_manager.get_cache_info()
    print(f"Cache now contains: {cache_info['total_files']} files, {cache_info['total_size_bytes']} bytes")
    
    # Test 2: Second load (with file cache)
    print("\n--- SECOND LOAD (With File Cache) ---")
    # Clear memory cache but keep file cache
    SpreadsheetLoader.clear_all_caches()
    print("Memory cache cleared, file cache retained")
    
    start_time = time.time()
    
    second_load_results = {}
    for song in test_songs:
        song_start = time.time()
        print(f"Loading {song}...")
        try:
            loader = SpreadsheetLoader(song)
            compiler = ActionCompiler(loader)
            actions = compiler.compile_actions()
            song_time = time.time() - song_start
            second_load_results[song] = {
                'success': True,
                'actions': len(actions),
                'time': song_time
            }
            print(f"  ✓ {song}: {len(actions)} actions loaded in {song_time:.2f}s (from file cache)")
        except Exception as e:
            song_time = time.time() - song_start
            second_load_results[song] = {
                'success': False,
                'actions': 0,
                'time': song_time
            }
            print(f"  ✗ {song}: Failed to load in {song_time:.2f}s - {e}")
    
    second_load_time = time.time() - start_time
    print(f"Total second load time: {second_load_time:.2f} seconds")
    
    # Test 3: Third load (with memory cache)
    print("\n--- THIRD LOAD (With Memory Cache) ---")
    start_time = time.time()
    
    third_load_results = {}
    for song in test_songs:
        song_start = time.time()
        print(f"Loading {song}...")
        try:
            loader = SpreadsheetLoader(song)
            compiler = ActionCompiler(loader)
            actions = compiler.compile_actions()
            song_time = time.time() - song_start
            third_load_results[song] = {
                'success': True,
                'actions': len(actions),
                'time': song_time
            }
            print(f"  ✓ {song}: {len(actions)} actions loaded in {song_time:.2f}s (from memory cache)")
        except Exception as e:
            song_time = time.time() - song_start
            third_load_results[song] = {
                'success': False,
                'actions': 0,
                'time': song_time
            }
            print(f"  ✗ {song}: Failed to load in {song_time:.2f}s - {e}")
    
    third_load_time = time.time() - start_time
    print(f"Total third load time: {third_load_time:.2f} seconds")
    
    # Show improvement comparison
    print(f"\n--- PERFORMANCE COMPARISON ---")
    print(f"1st load (no cache):     {first_load_time:.2f}s")
    print(f"2nd load (file cache):   {second_load_time:.2f}s")
    print(f"3rd load (memory cache): {third_load_time:.2f}s")
    
    if first_load_time > 0:
        file_improvement = ((first_load_time - second_load_time) / first_load_time) * 100
        memory_improvement = ((first_load_time - third_load_time) / first_load_time) * 100
        file_speedup = first_load_time / second_load_time if second_load_time > 0 else float('inf')
        memory_speedup = first_load_time / third_load_time if third_load_time > 0 else float('inf')
        
        print(f"\nFile cache improvement: {file_improvement:.1f}% ({file_speedup:.1f}x faster)")
        print(f"Memory cache improvement: {memory_improvement:.1f}% ({memory_speedup:.1f}x faster)")
        print(f"File cache vs memory cache: {((second_load_time - third_load_time) / second_load_time * 100):.1f}% difference")
    
    # Show detailed per-song comparison
    print(f"\n--- PER-SONG COMPARISON ---")
    for song in test_songs:
        if all(song in results for results in [first_load_results, second_load_results, third_load_results]):
            first = first_load_results[song]
            second = second_load_results[song]
            third = third_load_results[song]
            
            if first['success'] and second['success'] and third['success']:
                print(f"{song}:")
                print(f"  No cache:     {first['time']:.3f}s")
                print(f"  File cache:   {second['time']:.3f}s ({(first['time']/second['time']):.1f}x faster)")
                print(f"  Memory cache: {third['time']:.3f}s ({(first['time']/third['time']):.1f}x faster)")
    
    # Test cache clearing
    print("\n--- TESTING CACHE CLEARING ---")
    cache_manager.clear_cache()
    SpreadsheetLoader.clear_all_caches()
    print("All caches cleared successfully")
    
    # Final cache info
    final_cache_info = cache_manager.get_cache_info()
    print(f"Final cache state: {final_cache_info['total_files']} files")
    
    print("\n" + "=" * 60)
    print("FILE-BASED CACHING TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_caching_performance()
