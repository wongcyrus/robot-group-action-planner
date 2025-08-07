# Excel Export Feature for Robot Actions

## Overview

The robot action compiler now exports beautifully formatted Excel files instead of CSV for much better readability and action design workflow. Excel files provide superior formatting, styling, and readability for complex multiline action sequences.

## Key Features

### 📊 **Professional Excel Formatting**
- **Color-coded headers**: Blue background with white text for easy identification
- **Styled columns**: Different background colors for Time vs Robot columns
- **Auto-sized columns**: Optimal width for each column type
- **Wrapped text**: Multiline actions display properly in cells
- **Auto-height rows**: Automatically adjusts row height for multiline content

### ⏱️ **Enhanced Duration Display**
- **Total time first**: `⏱️ TOTAL: total_time s` shown prominently at the top of each cell
- **Individual action durations**: `action_name (duration_seconds)` for each action
- **Easy calculation verification**: Quickly see total time before reading individual actions
- **Highlighted formatting**: Total time displayed in blue bold text for easy identification

### 🎨 **Visual Organization**
- **Time column**: Light blue background, centered, bold text
- **Robot columns**: Light background with left-aligned, wrapped text
- **Header row**: Dark blue background with white bold text
- **Professional styling**: Easy to read and print

## File Structure

```
data/
├── compiled_actions_test-dance.xlsx    # Excel files with formatting
├── compiled_actions_06-90.xlsx         # Professional layout
├── robot_actions_*.json                # Existing JSON cache
└── action_details_*.json               # Existing action details
```

## Export Examples

### Command Line Export
```bash
# Export to data folder with auto-generated filename
python export_actions_excel.py test-dance

# Export to specific location
python export_actions_excel.py test-dance my_choreography.xlsx

# With debug logging
python export_actions_excel.py --log-level DEBUG 06-90
```

### Programmatic Export
```python
from core.action_compiler import ActionCompiler
from core.spreadsheet_loader import SpreadsheetLoader

loader = SpreadsheetLoader("my-song")
compiler = ActionCompiler(loader)

# Export to data folder with auto-generated filename
excel_path = compiler.export_compiled_actions_to_excel(song_name="my-song")

# Or compile and export together
actions = compiler.compile_actions(export_csv=True, song_name="my-song")
```

## Excel Cell Format Example

```
Humanoid_1 column:
┌─────────────────────────────────┐
│ ⏱️ TOTAL: 11.5 s                │
│ wave (3.5)                      │
│ bow (4.0)                       │
│ right_kick (2.0)                │
│ left_kick (2.0)                 │
└─────────────────────────────────┘

Time column:     Drone_1 column:
┌─────────┐      ┌─────────────────┐
│   4.0   │      │ ⏱️ TOTAL: 3.0 s │
│         │      │ takeoff (3.0)   │
└─────────┘      └─────────────────┘
```

## Styling Details

### Header Row
- **Background**: Dark blue (#366092)
- **Font**: Bold white text
- **Alignment**: Centered

### Time Column
- **Background**: Light blue (#E6F3FF)
- **Font**: Bold black text
- **Alignment**: Centered
- **Width**: 8 characters

### Robot Columns (Humanoid_, Drone_, Dog_)
- **Background**: Very light blue (#F0F8FF)
- **Font**: Regular black text
- **Alignment**: Left-aligned, top-aligned
- **Text wrapping**: Enabled
- **Width**: 25 characters
- **Height**: Auto-adjusts for multiline content

### Total Time Display
- **Format**: `⏱️ TOTAL: total_time s` at the beginning of each cell
- **Purpose**: Immediate visibility of total time calculations
- **Style**: Bold blue text with clock emoji for instant recognition
- **Position**: First line of each robot cell for maximum visibility

## Integration with Main Pipeline

The main application (`main.py`) automatically generates Excel cache files during song preloading:

```python
# In main.py - _preload_all_song_data()
robot_actions = action_compiler.compile_actions(export_csv=True, song_name=song_name)
```

This creates professionally formatted Excel files for each song automatically.

## Backward Compatibility

- **Legacy CSV method**: `export_compiled_actions_to_csv()` now redirects to Excel export
- **Parameter compatibility**: All existing parameters work unchanged
- **Main pipeline**: No changes needed to existing code

## Benefits Over CSV

1. **Readability**: Color coding and formatting make complex sequences easy to read
2. **Cell formatting**: Multiline actions display properly without escaping issues
3. **Visual organization**: Different column types are clearly distinguished
4. **Professional output**: Suitable for documentation and sharing with teams
5. **Excel features**: Can be opened in Excel, LibreOffice, Google Sheets
6. **Print-friendly**: Professional formatting looks good when printed
7. **Total calculations**: Easy to verify time totals at a glance

## Technical Implementation

- **Library**: Uses `openpyxl` for Excel file generation
- **File format**: Modern .xlsx format (Excel 2007+)
- **Compatibility**: Works with Excel, LibreOffice Calc, Google Sheets
- **Performance**: Efficient generation even for large action sequences
- **Memory usage**: Minimal memory footprint during export

## Dependencies

The Excel export feature requires:
```
openpyxl>=3.0.0
```

This is automatically installed when running the export functionality.

## File Locations

- **Auto-generated files**: Saved to `data/compiled_actions_{song_name}.xlsx`
- **Custom paths**: Support for any custom output location
- **Cache integration**: Works seamlessly with existing cache system

The Excel export feature transforms complex robot action sequences into beautifully formatted, professional-looking spreadsheets that are perfect for action design, review, and documentation! 📊✨
