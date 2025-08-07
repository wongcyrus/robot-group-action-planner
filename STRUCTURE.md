# Reorganized Project Structure

## Project Overview
The Robot Group Action Planner has been reorganized for maximum clarity and maintainability.

## Directory Structure

```
robot-group-action-planner/
├── main.py                    # 🚀 Application entry point
├── constant.py               # 📊 Global constants and configuration values
│
├── config/                   # ⚙️ Configuration management
│   ├── settings.py          # Application settings and config classes
│   └── __init__.py
│
├── core/                     # 🧠 Core data processing modules
│   ├── action_compiler.py   # Compiles and validates robot actions
│   ├── cache_manager.py     # Manages data caching functionality
│   ├── spreadsheet_loader.py # Loads data from Google Spreadsheets
│   └── __init__.py
│
├── robot_types/             # 🤖 Robot action implementations
│   ├── base_action.py       # Abstract base class for all robots
│   ├── humanoid_action.py   # Humanoid robot actions
│   ├── dog_action.py        # Dog robot actions
│   ├── drone_action.py      # Drone robot actions
│   └── __init__.py
│
├── robot_hardware/          # 🔧 Hardware drivers and interfaces
│   ├── djitellopy/          # DJI Tello drone drivers
│   ├── dog/                 # Dog robot hardware drivers
│   └── __init__.py
│
├── robot_factory/           # 🏭 Robot creation and management
│   ├── factory.py           # Factory pattern for robot creation
│   └── __init__.py
│
├── playback/                # 🎵 Execution and media management
│   ├── engine.py            # Action execution engine
│   ├── manager.py           # Media playback manager
│   └── __init__.py
│
├── data/                    # 💾 Data storage (cache and logs)
│   ├── [cache files]       # Cached spreadsheet data
│   ├── [log files]         # Application and robot logs
│   └── __init__.py
│
├── songs/                   # 🎶 Media files for choreography
│   └── [song files]        # .mp4 files for robot performances
│
├── tools/                   # 🛠️ Utility scripts and helpers
│   ├── cache_utils.py       # Cache management utilities
│   ├── log_utils.py         # Logging utilities
│   └── __init__.py
│
├── docs/                    # 📚 Documentation and guides
│   └── [documentation files]
│
└── StanfordQuadruped/       # 🐕 Stanford Quadruped specific files
    └── [quadruped files]
```

## Key Improvements

### 🎯 **Clear Separation of Concerns**
- **`core/`** - Pure data processing logic
- **`robot_types/`** - Robot behavior implementations  
- **`robot_hardware/`** - Hardware communication drivers
- **`robot_factory/`** - Object creation patterns
- **`playback/`** - Execution and media coordination

### 📁 **Logical Grouping**
- **`data/`** - All persistent data (cache + logs)
- **`tools/`** - Utilities and helper scripts
- **`songs/`** - Media files with proper naming

### 🔧 **Easy to Navigate**
- Meaningful directory names that describe their purpose
- Clear file organization within each module
- Removed duplicate/nested project directories

### 🚀 **Maintainable Architecture**
- Easy to find where specific functionality lives
- Simple to add new robot types or modify existing ones
- Clear dependency relationships between modules

## Import Structure

```python
# Main application
from core.action_compiler import ActionCompiler
from robot_factory.factory import RobotFactory
from playback.engine import ExecutionEngine

# Robot implementations
from robot_types.dog_action import DogAction
from robot_types.drone_action import DroneAction

# Hardware drivers
from robot_hardware.djitellopy import Tello
```

This structure makes it immediately clear where to find and modify specific functionality, while maintaining clean separation between different concerns of the system.
