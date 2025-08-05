# File-Based Caching Quick Start Guide

## Configuration

The file-based caching system is controlled by constants in `constant.py`:

```python
# Enable or disable file caching
USE_FILE_CACHE = True

# Directory to store cache files (relative to project root)
CACHE_DIRECTORY = "cache"

# Cache expiration time in hours (0 = never expire)
CACHE_EXPIRY_HOURS = 24
```

## How It Works

1. **First Run**: Data is loaded from Google Sheets and cached to files
2. **Subsequent Runs**: Data is loaded from cache files (much faster)
3. **Expiry**: Old cache files are automatically cleaned up

## Usage

### Normal Operation
```bash
# Run the application normally - caching is automatic
python main.py
```

### Cache Management
```bash
# View cache status and files
python cache_utils.py info

# Test cache performance
python cache_utils.py test

# Clear all cache files
python cache_utils.py clear

# Remove only expired files
python cache_utils.py cleanup
```

## Performance Expectations

| Scenario | Loading Time | Notes |
|----------|--------------|-------|
| First run (no cache) | Baseline | Normal Google Sheets loading |
| File cache hit | 70-90% faster | Data loaded from disk |
| Memory cache hit | 95-99% faster | Data already in memory |

## Cache File Structure

Cache files are stored as JSON in the `cache/` directory:
```
cache/
├── a1b2c3d4.json  # Action details cache
├── e5f6g7h8.json  # Robot actions for song 1
├── i9j0k1l2.json  # Robot actions for song 2
└── ...
```

Each cache file contains:
```json
{
  "cache_key": "robot_actions_06-90_spreadsheet_id",
  "timestamp": 1722873600.0,
  "data": { ... }
}
```

## Troubleshooting

### Cache Not Working
1. Check `USE_FILE_CACHE = True` in `constant.py`
2. Ensure write permissions to project directory
3. Check logs for cache-related errors

### Stale Data
1. Clear cache: `python cache_utils.py clear`
2. Reduce `CACHE_EXPIRY_HOURS` value
3. Restart application

### Large Cache Size
1. Run cleanup: `python cache_utils.py cleanup`
2. Clear old caches: `python cache_utils.py clear`
3. Reduce `CACHE_EXPIRY_HOURS` value

## Development Tips

- Use `python cache_utils.py test` to verify caching is working
- Monitor cache hit rates in application logs
- Clear cache when testing spreadsheet changes
- Use shorter expiry times during development
