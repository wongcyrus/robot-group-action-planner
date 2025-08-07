# Enhanced NetworkDogAction with MovementGroups Integration

## Overview

The `NetworkDogAction` class has been enhanced to directly integrate with Stanford Quadruped Mini Pupper's `MovementGroups` API, eliminating the need for action name mapping and providing direct access to all movement functions.

## Key Changes

### 1. Removed Action Mapping
- **Before**: Complex action name mapping from generic names to robot-specific commands
- **After**: Direct use of MovementGroups function names (e.g., `move_forward`, `look_up`, `body_cycle`)

### 2. Updated Network Action Server
- Enhanced to use `MovementGroups` class directly
- Automatically discovers all available movement functions
- Provides rich movement capabilities with proper parameter handling

### 3. Available MovementGroups Actions

#### Basic Movement Actions
- `stop(time)` - Return to default standing position
- `move_forward()` - Move forward at 0.15m/s
- `move_backward()` - Move backward at 0.15m/s
- `move_left()` - Move left at 0.15m/s
- `move_right()` - Move right at 0.15m/s
- `move_leftfront()` - Move diagonal left-forward
- `move_rightfront()` - Move diagonal right-forward
- `move_leftback()` - Move diagonal left-backward
- `move_rightback()` - Move diagonal right-backward

#### Head/Looking Actions
- `look_up()` - Look up 20 degrees
- `look_down()` - Look down 20 degrees
- `look_left()` - Look left 30 degrees
- `look_right()` - Look right 30 degrees
- `look_upperleft()` - Look up and left
- `look_upperright()` - Look up and right
- `look_leftlower()` - Look down and left
- `look_rightlower()` - Look down and right

#### Advanced Movement Actions
- `head_move(pitch_deg, yaw_deg, time_uni, time_acc)` - Custom head movement
- `body_row(row_deg, time_uni, time_acc)` - Body rolling movement
- `balance(roll_deg, pitch_deg, time_uni, time_acc)` - Balance with roll/pitch
- `gait_uni(v_x, v_y, time_uni, time_acc)` - Custom velocity movement
- `height_move(ht, time_uni, time_acc)` - Vertical height adjustment

#### Leg Movement Actions
- `foreleg_lift(leg_index, ht, time_uni, time_acc)` - Lift front leg
- `backleg_lift(leg_index, ht, time_uni, time_acc)` - Lift back leg

#### Special Movement Actions
- `rotate(angle)` - Rotate around body center
- `bowback(angle)` - Bow head and move backward
- `body_cycle()` - Draw circle with body center
- `head_ellipse()` - Draw ellipse with head movement

## Usage Examples

### Basic Usage
```python
from actions.enhanced_dog_action import NetworkDogAction

# Define action timings using MovementGroups function names
action_timings = {
    "move_forward": 3.0,
    "look_up": 2.0,
    "body_cycle": 5.0,
    "stop": 1.0,
}

# Create dog action handler
dog = NetworkDogAction(
    action_name_to_time=action_timings,
    robot_ip="10.0.0.10",
    robot_api_port=8080
)

# Execute actions directly
dog.execute_action_sync("move_forward")
dog.execute_action_sync("look_up")
dog.execute_action_sync("body_cycle")
dog.execute_action_sync("stop")
```

### Advanced Usage with Parameters
```python
# The network action server handles MovementGroups parameters automatically
# For example, head_move will receive pitch_deg, yaw_deg parameters
# gait_uni will receive v_x, v_y parameters
# All based on the action name and predefined parameter sets
```

## Network Action Server Updates

The `network_action_server.py` has been updated to:

1. **Import MovementGroups**: Automatically loads the MovementGroups class
2. **Dynamic Action Discovery**: Scans MovementGroups for available functions
3. **Parameter Handling**: Maps parameters to appropriate MovementGroups function signatures
4. **Direct Execution**: Calls MovementGroups functions directly without UDP mapping

## Benefits

1. **No Mapping Required**: Direct use of MovementGroups function names
2. **Full Feature Access**: All MovementGroups capabilities available
3. **Type Safety**: Proper parameter types and validation
4. **Extensibility**: New MovementGroups functions automatically available
5. **Cleaner Code**: Removed complex mapping logic

## Migration from Old System

### Old Way (with mapping)
```python
# Had to use generic names that were mapped
action_timings = {
    "walk_forward": 3.0,    # Mapped to "forward"
    "look_up": 2.0,         # Mapped to "pitch_up"
    "dance_move": 5.0,      # Mapped to "dance"
}
```

### New Way (direct MovementGroups)
```python
# Use actual MovementGroups function names
action_timings = {
    "move_forward": 3.0,    # Direct MovementGroups function
    "look_up": 2.0,         # Direct MovementGroups function
    "body_cycle": 5.0,      # Direct MovementGroups function
}
```

## Testing

Run the test script to verify all functions work:

```bash
python test_enhanced_dog_action.py
```

This will test all major MovementGroups actions and demonstrate the new direct integration.
