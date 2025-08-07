# CSV Cache Implementation

## Overview

The CSV export functionality has been enhanced to automatically save compiled action files to the `data` folder as cache. This provides several benefits:

## Key Features

### 🗂️ **Automatic Data Folder Storage**
- All CSV exports are now saved to the `data` folder by default
- Cache files are stored alongside other project data (JSON cache files)
- Consistent file organization and easy access

### ⏱️ **Enhanced Duration Display**
- Each action shows individual duration: `action_name (duration)`
- Each cell shows total time at the end: `[total_time s]`
- Example format:
  ```
  move_forward (1.1)
  move_backward (1.1) 
  turn_left (2.0)
  [4.2 s]
  ```

### 📁 **Smart Filename Generation**
- Cache-friendly filenames: `compiled_actions_{song_name}.csv`
- Examples:
  - `compiled_actions_test-dance.csv`
  - `compiled_actions_06-90.csv`
  - `compiled_actions_my-choreography.csv`

### 🔄 **Integration with Main Pipeline**
- `main.py` now automatically exports CSV cache during song data preloading
- Each song gets a corresponding CSV cache file during initialization
- No manual intervention required for cache generation

## Implementation Details

### Enhanced `ActionCompiler` Methods

#### `export_compiled_actions_to_csv(output_path, song_name)`
- **Auto-path generation**: If `output_path` is None, automatically creates path in data folder
- **Song name integration**: Uses `song_name` parameter for cache-friendly filenames
- **Directory creation**: Automatically creates the data folder if it doesn't exist

#### `compile_actions(export_csv, csv_path, song_name)`
- **New parameter**: `song_name` for better cache filename generation
- **Automatic export**: When `export_csv=True`, saves to data folder by default
- **Enhanced logging**: Shows cache location in log messages

### Updated Main Pipeline

```python
# In main.py - _preload_all_song_data()
robot_actions = action_compiler.compile_actions(export_csv=True, song_name=song_name)
```

- CSV cache files are automatically generated during preloading
- No performance impact on main execution
- Cache files are available for external analysis

## File Structure

```
robot-group-action-planner/
├── data/
│   ├── compiled_actions_test-dance.csv      # New CSV cache
│   ├── compiled_actions_06-90.csv           # New CSV cache
│   ├── robot_actions_test-dance_*.json      # Existing JSON cache
│   ├── robot_actions_06-90_*.json           # Existing JSON cache
│   └── action_details_*.json                # Existing action details
├── export_actions_csv.py                    # Updated command-line tool
└── main.py                                  # Updated to auto-generate cache
```

## Usage Examples

### Automatic Cache Generation (Main Pipeline)
```python
# Cache files are automatically created during preloading
python main.py  # CSV files saved to data/ folder automatically
```

### Manual Export (Command Line)
```bash
# Export to data folder with auto-generated filename
python export_actions_csv.py test-dance

# Export to specific location
python export_actions_csv.py test-dance custom_output.csv
```

### Programmatic Export
```python
from core.action_compiler import ActionCompiler
from core.spreadsheet_loader import SpreadsheetLoader

loader = SpreadsheetLoader("my-song")
compiler = ActionCompiler(loader)

# Auto-save to data folder
csv_path = compiler.export_compiled_actions_to_csv(song_name="my-song")

# Or compile and export together
actions = compiler.compile_actions(export_csv=True, song_name="my-song")
```

## Benefits

1. **Consistent Organization**: All cache files in one location
2. **Automatic Generation**: No manual steps required
3. **Performance**: Cache files ready for analysis without recompilation
4. **Enhanced Duration Info**: Individual action times plus total cell time
5. **Action Design Support**: Easy to see if action sequences fit time constraints
6. **Integration**: Seamless integration with existing caching system
7. **Flexibility**: Still supports custom output paths when needed

## Backward Compatibility

- All existing code continues to work unchanged
- New parameters are optional with sensible defaults
- Export tools work with both auto-generated and custom paths

## Cache Management

CSV cache files follow the same pattern as existing JSON cache:
- Stored in the `data` folder
- Named with song identifiers
- Can be safely deleted and regenerated
- No expiration (unlike some JSON cache files)

This implementation provides a robust, integrated caching solution for CSV exports while maintaining full backward compatibility.
