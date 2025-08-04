# Robot Dog Integration

This document explains how to integrate and use 2 robot dogs with the robot-group-action-planner system.

## Overview

The system has been enhanced to support robot dogs alongside the existing drones and humanoid robots. The implementation includes:

- `DogAction` class: Provides a unified interface for robot dog operations
- Integration with the main action planning system
- Support for coordinated multi-dog performances
- Demo script for testing and examples

## Files Added/Modified

### New Files
- `dog_action.py`: Main interface for robot dog actions
- `dog_demo.py`: Demonstration script showing dog capabilities

### Modified Files
- `main.py`: Added dog initialization and execution logic
- `constant.py`: Added dog robot configuration constants

## Configuration

### Dog Robot Settings (constant.py)
```python
# Dog robot configuration
DOG_IPS = ["192.168.137.8", "192.168.137.9"]  # IP addresses for 2 dog robots
DOG_PORTS = [8830, 8830]  # UDP ports for dog robots
SKIP_DOGS = False  # Set to True to skip dog initialization
```

### Spreadsheet Columns
When using the main planning system, add columns to your spreadsheet for dog actions:
- `Dog_1`: Actions for the first dog robot
- `Dog_2`: Actions for the second dog robot

## Supported Dog Actions

### Basic Movement
- `forward`, `forward_50` (with distance)
- `back`, `back_30` (with distance)
- `left`, `left_25` (with distance)
- `right`, `right_40` (with distance)

### Rotation
- `cw`, `cw_90` (clockwise with angle)
- `ccw`, `ccw_45` (counter-clockwise with angle)
- `rotate_cw_180`, `rotate_ccw_90` (alternative syntax)

### Posture Control
- `activate`: Activate the robot
- `stand_up`: Make the robot stand up
- `lay_down`: Make the robot lay down
- `deactivate`: Deactivate the robot

### Special Actions
- `hop`, `hop_2.5` (with duration)
- `stop`: Stop all movement
- `dance`, `dance_3.0` (with duration)

### Advanced Actions
- `custom_movement_x_0.5_y_0.3_duration_2.0`: Custom movement with parameters

## Usage Examples

### Basic Integration with Main System

The dogs are automatically initialized when you run the main system:

```python
# In your spreadsheet, add columns Dog_1 and Dog_2
# Example row:
# Time | Robot_1 | Drone_1 | Dog_1      | Dog_2
# 3.0  | wave    | takeoff | stand_up   | stand_up
# 2.0  | dance   | hover   | forward_50 | back_50
```

### Programmatic Control

```python
from dog.action_executor import DogActionExecutor
from dog_action import DogAction

# Initialize a dog
dog_executor = DogActionExecutor(
    robot_name="dog_1",
    robot_ip="192.168.137.8",
    robot_port=8830
)

action_mappings = {
    "stand_up": 2.0,
    "forward": 2.0,
    "hop": 1.5,
}

dog_action = DogAction(
    dog_executor,
    action_mappings,
    {},
    "dog_1"
)

# Execute actions
dog_action.run_action("stand_up")
dog_action.run_action("forward_100")
dog_action.run_action("hop")
```

### Running the Demo

```bash
python dog_demo.py
```

The demo includes:
1. **Synchronized Actions**: Both dogs perform the same actions simultaneously
2. **Alternating Actions**: Dogs take turns performing different actions
3. **Coordinated Dance**: Complex choreography with different moves per dog

## Action Parameters

### Distance Parameters
Actions can include distance specifications:
- `forward_50`: Move forward 50 units
- `left_30`: Move left 30 units
- Default distance: 50 units if not specified

### Angle Parameters
Rotation actions can include angle specifications:
- `cw_90`: Rotate clockwise 90 degrees
- `ccw_180`: Rotate counter-clockwise 180 degrees
- Default angle: 90 degrees if not specified

### Speed Parameters
Movement actions can include speed:
- `forward_50_0.7`: Move forward 50 units at 70% speed
- Valid speed range: 0.1 to 1.0
- Default speed: 0.5

### Duration Parameters
Timed actions can include duration:
- `hop_2.5`: Hop for 2.5 seconds
- `dance_5.0`: Dance for 5.0 seconds
- Valid duration range: 0.1 to 10.0 seconds

## Error Handling

The system includes comprehensive error handling:

- **Connection Errors**: Logs failure to connect to dog robots
- **Action Failures**: Logs failed action executions
- **Emergency Stop**: `emergency_stop()` method for immediate halt
- **Status Monitoring**: `get_status()` method for real-time status

## Timing and Synchronization

### Default Action Times
```python
activate/deactivate: 1.0s
stand_up/lay_down: 2.0s
movement actions: 2.0s
rotation actions: 2.0s
hop: 1.5s
stop: 0.5s
dance: 3.0s
custom_movement: 2.0s
```

### Coordinated Execution
- Actions are executed in separate threads for parallelism
- `stop_event` parameter allows for graceful interruption
- Thread synchronization ensures coordinated performance

## Troubleshooting

### Common Issues

1. **Dogs not initializing**
   - Check IP addresses and network connectivity
   - Verify UDP port availability
   - Ensure dog robots are powered on and in range

2. **Actions not executing**
   - Check dog robot status with `get_status()`
   - Verify action names are correctly spelled
   - Check for error messages in logs

3. **Timing issues**
   - Adjust action timing in spreadsheet or action mappings
   - Check for network latency affecting UDP communication
   - Use `emergency_stop()` if dogs become unresponsive

### Debug Mode
Enable debug logging for detailed information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing System

The dog integration is designed to work seamlessly with existing robots and drones:

- **Non-blocking**: Dog actions don't interfere with other robot types
- **Unified Timing**: All robots follow the same timing system
- **Skip Option**: Set `SKIP_DOGS = True` to disable dogs without affecting other robots
- **Thread-safe**: Multiple robot types can operate simultaneously

## Future Enhancements

Potential improvements for the dog robot system:

1. **Advanced Choreography**: More complex movement patterns
2. **Sensor Integration**: Obstacle avoidance and environmental awareness
3. **Formation Control**: Maintain specific positions relative to each other
4. **Voice Commands**: Integration with speech recognition
5. **Computer Vision**: Visual tracking and following behaviors

## Support

For issues or questions about the dog robot integration:

1. Check the logs for error messages
2. Verify network configuration and connectivity
3. Test with the demo script first
4. Review the dog folder documentation for API details
