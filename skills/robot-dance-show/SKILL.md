---
name: robot-dance-show
description: Manage and execute robot dance performances. This skill is fully self-contained, providing its own internal orchestration scripts and bypassing root-level entry points like main.py or run.sh.
---

# Robot Dance Show

## Overview

The `robot-dance-show` skill is a modular package for coordinating robot dance performances. It encapsulates all the necessary procedural knowledge and execution tools within its own folder, ensuring a consistent and isolated workflow.

## Core Mandates

- **Do NOT** use root-level scripts like `main.py` or `run.sh`.
- **Use Internal Tools**: Always use the skill's internal runner script for performances.
- **Maintain Isolation**: Ensure that changes to project-level entry points do not affect the performance logic provided by this skill.

## Workflow

### 1. Discovery
Use the skill's internal discovery script to see which performances are ready.
```bash
./skills/robot-dance-show/scripts/list_songs.sh
```

### 2. Preparation
Ensure the robot configurations (IPs, types) are correctly set in `config/settings.py`.

### 3. Execution
Execute a performance using the skill's private launcher script. This script automatically locates and uses the project's virtual environment to ensure all dependencies are available.

```bash
./skills/robot-dance-show/scripts/launcher.sh "<SONG_NAME>"
```

### 4. Monitoring & Debugging
The performance logs are handled via the centralized logging system. If you encounter timing or synchronization issues, consult the skill's internal documentation.

## References
For a detailed look at the skill's self-contained architecture and project integration:
- See [architecture.md](references/architecture.md)

## Capabilities

### Modular Orchestration
- **Encapsulated Runner**: A dedicated execution script specifically for dance shows.
- **Project Integration**: Seamlessly imports `core` and `hardware` modules while remaining independent of root scripts.

### Performance Management
- **Song Targeting**: Targeted execution of specific choreographies.
- **Resource Coordination**: Managing the synchronization of dogs, drones, and humanoid robots.
