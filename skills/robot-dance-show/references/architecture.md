# Robot Dance Show Architecture

This document describes how the `robot-dance-show` skill interfaces with the project while maintaining complete self-containment.

## Self-Containment Strategy

To ensure that the skill is modular and does not rely on project-level entry points (like `main.py`), the following design principles are applied:

1.  **Internal Runner**: The skill provides its own Python script at `scripts/dance_runner.py`. This script is the sole entry point for performances triggered by this skill.
2.  **Path Resolution**: The internal runner dynamically adds the project root to the Python path, allowing it to use `core`, `config`, and `robot_hardware` modules without being located in the root directory.
3.  **Instruction Isolation**: The `SKILL.md` instructions only reference the skill's internal scripts. It specifically forbids the use of root-level execution scripts.

## Integration Points

The skill interacts with the following project components via direct module imports:

- **`config/`**: To retrieve robot IP addresses and system settings.
- **`core/`**: To utilize the `ActionCompiler` and `SpreadsheetLoader` for processing choreography data.
- **`robot_hardware/`**: To communicate with physical robot hardware (Tello drones, Unitree dogs, etc.).
- **`songs/`**: To access the media files required for the show.

## Environment Requirements

- **Virtual Environment**: Must be activated (`source venv/bin/activate`).
- **Dependencies**: All packages listed in the root `requirements.txt` must be installed.
- **Working Directory**: The skill's runner script must be executed from the project root to ensure consistent relative path resolution.
