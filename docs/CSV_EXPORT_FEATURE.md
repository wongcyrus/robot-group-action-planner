# CSV Export Feature

## Overview

The Robot Action Planner now supports exporting compiled actions to CSV format with duration annotations. This feature is useful for:

- **Action Design**: Review action sequences with their durations for timing optimization
- **Documentation**: Create readable spreadsheets showing robot choreography
- **Analysis**: Import into external tools for further analysis
- **Sharing**: Distribute action sequences in a standard format

## Features

- **Duration Annotations**: Each action shows its execution time in parentheses
  - Example: `move_forward (1.1)` means the action takes 1.1 seconds
- **Multiline Cell Support**: Actions that span multiple lines are preserved
- **All Robot Types**: Supports Humanoid, Drone, and Dog actions
- **Standard CSV Format**: Compatible with Excel, Google Sheets, and other tools

## Usage

### Method 1: Direct Export

```python
from core.action_compiler import ActionCompiler
from core.spreadsheet_loader import SpreadsheetLoader

# Initialize components
loader = SpreadsheetLoader("your-spreadsheet-id")
compiler = ActionCompiler(loader)

# Export to CSV
csv_file = compiler.export_compiled_actions_to_csv("my_actions.csv")
print(f"Exported to: {csv_file}")
```

### Method 2: Compile and Export Together

```python
# Compile actions and export in one step
actions = compiler.compile_actions(export_csv=True, csv_path="choreography.csv")
```

### Method 3: Command Line Tool

Use the dedicated export script:

```bash
# Export specific spreadsheet
python export_actions_csv.py test-dance

# Export with custom filename
python export_actions_csv.py 06-90 my_choreography.csv

# Export with debug logging
python export_actions_csv.py --log-level DEBUG test-dance debug_output.csv
```

## CSV Format Example

```csv
Time,Humanoid_1,Humanoid_2,Drone_1,Drone_2,Dog_1,Dog_2
4,wave (3.5),bow (4.0),takeoff (3.0),takeoff (3.0),move_forward (1.1),move_backward (1.1)
4,wave (3.5),bow (4.0),move_back (3.0),move_back (3.0),move_backward (1.1),move_backward (1.1)
59,"right_kick (2.0)
left_kick (2.0)
right_uppercut (2.0)",bow (4.0),land (3.0),land (3.0),sit (2.0),sit (2.0)
```

## Key Benefits

1. **Duration Visibility**: Immediately see how long each action takes
2. **Timing Validation**: Easily spot actions that exceed their time allocation
3. **Universal Format**: CSV works with any spreadsheet application
4. **Action Planning**: Design sequences with precise timing information
5. **Documentation**: Create clear records of robot choreographies

## Files Created

- Default filename: `compiled_actions_{spreadsheet_name}.csv`
- Custom filename: As specified in the method call
- Location: Current working directory (unless absolute path specified)

## Error Handling

- Missing actions show duration `(0)` and are logged as warnings
- Invalid time values are handled gracefully
- Jinja2 templates in actions are rendered before export
- File creation errors are logged with detailed information

## Integration

The CSV export feature integrates seamlessly with existing workflows:

- **Backward Compatible**: Existing `compile_actions()` calls continue to work
- **Optional Feature**: Export only happens when explicitly requested
- **Logging Integration**: Uses the same logging system as other components
- **Cache Friendly**: Works with cached spreadsheet data for faster exports
