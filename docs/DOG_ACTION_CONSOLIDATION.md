# Enhanced Dog Action Integration Documentation

## Overview

The Robot Group Action Planner includes an enhanced dog action implementation for the Stanford Quadruped Mini Pupper robot. The `DogAction` class has been consolidated and enhanced to provide better network communication, improved error handling, and direct MovementGroups integration while maintaining backwards compatibility.

## Architecture

### Current Setup
```
PC (Robot Group Action Planner) <--HTTP API--> Mini Pupper Robot (Network Action Server) <--Direct--> Stanford Quadruped MovementGroups
```

### Components

1. **DogAction Class** (`actions/dog_action.py`)
   - Consolidated enhanced dog action implementation
   - Runs on the PC client
   - Communicates with robot via HTTP API
   - Direct MovementGroups integration without complex mapping
   - Provides backwards compatibility

2. **Network Action Server** (`network_action_server.py`)
   - Runs on the Mini Pupper robot
   - Provides RESTful HTTP API for remote control
   - Direct integration with MovementGroups class
   - Manages action queuing and execution

3. **Setup Script** (`setup_enhanced_network_server.py`)
   - Installs and configures the network server on the robot
   - Creates systemd service for automatic startup
   - Provides easy deployment

## What Was Done - Consolidation

### 1. Enhanced DogAction Class
- **Location**: `actions/dog_action.py`
- **Features**: Combined all functionality from previous separate classes
- **Capabilities**: Direct MovementGroups integration, network API communication, no action mapping needed

### 2. Backwards Compatibility File
- **Kept**: `actions/enhanced_dog_action.py` 
- **Purpose**: Provides backwards compatibility aliases (`NetworkDogAction = DogAction`)
- **Impact**: Existing code importing from `enhanced_dog_action` continues to work

### 3. Key Features Combined

#### Network Integration
- HTTP API communication with robot
- Connection health monitoring
- Automatic retry and error handling
- Queue management and emergency stop

#### MovementGroups Integration
- Direct access to all MovementGroups functions
- Intelligent parameter mapping
- No complex action name mapping required
- Direct use of MovementGroups function names (e.g., `move_forward`, `look_up`, `body_cycle`)

#### Backwards Compatibility
- Supports all legacy parameters (`robot_port`, `dog_executor`, etc.)
- Automatic port conversion (UDP to API)
- Maintains existing interfaces

## Key Improvements

### 1. Better Network Communication
- **HTTP/REST API** instead of direct UDP manipulation
- **Reliable error handling** with proper status codes
- **Connection health monitoring** with automatic reconnection
- **Action parameter optimization** based on duration and context

### 2. Enhanced Action Management
- **Action queuing** for sequential execution
- **Real-time status monitoring** of robot state
- **Emergency stop** functionality
- **Direct MovementGroups access** without complex mapping

### 3. Improved Error Handling
- **Connection timeout** management
- **Graceful degradation** when robot is unreachable
- **Detailed logging** for debugging
- **Status feedback** for better monitoring

### 4. Direct MovementGroups Integration
- **No Mapping Required**: Direct use of MovementGroups function names
- **Full Feature Access**: All MovementGroups capabilities available
- **Type Safety**: Proper parameter types and validation
- **Extensibility**: New MovementGroups functions automatically available

## Valid Dog Actions for Spreadsheet Cells

The following actions can be used in your Google Spreadsheet cells:

### **Basic Movement Actions**
- `stop` - Return to default standing position
- `move_forward` - Move forward at 0.15m/s
- `move_backward` - Move backward at 0.15m/s
- `move_left` - Move left at 0.15m/s
- `move_right` - Move right at 0.15m/s
- `move_leftfront` - Move diagonal left-forward
- `move_rightfront` - Move diagonal right-forward
- `move_leftback` - Move diagonal left-backward
- `move_rightback` - Move diagonal right-backward

### **Head/Looking Actions**
- `look_up` - Look up 20 degrees
- `look_down` - Look down 20 degrees
- `look_left` - Look left 30 degrees
- `look_right` - Look right 30 degrees
- `look_upperleft` - Look up and left
- `look_upperright` - Look up and right
- `look_leftlower` - Look down and left
- `look_rightlower` - Look down and right

### **Advanced Movement Actions**
- `head_move` - Custom head movement (with pitch_deg, yaw_deg parameters)
- `body_row` - Body rolling movement (with row_deg parameter)
- `balance` - Balance with roll/pitch (with roll_deg, pitch_deg parameters)
- `gait_uni` - Custom velocity movement (with v_x, v_y parameters)
- `height_move` - Vertical height adjustment (with ht parameter)

### **Leg Movement Actions**
- `foreleg_lift` - Lift front leg (with leg_index, ht parameters)
- `backleg_lift` - Lift back leg (with leg_index, ht parameters)

### **Special Movement Actions**
- `rotate` - Rotate around body center (with angle parameter)
- `bowback` - Bow head and move backward (with angle parameter)
- `body_cycle` - Draw circle with body center
- `head_ellipse` - Draw ellipse with head movement

### **Legacy Actions (still supported)**
These legacy action names are still supported for backwards compatibility:
- `forward` - Basic forward movement
- `back` - Basic backward movement  
- `left` - Basic left movement
- `right` - Basic right movement
- `sit` - Sit position
- `stand` - Stand position
- `lay_down` - Lay down position
- `activate` - Activate/toggle activation
- `walk_mode` - Toggle walking mode
- `dance_mode` - Toggle dancing mode

### **Action Notes**
- **Case Insensitive**: Action names are processed in lowercase
- **Default Timing**: Actions not in spreadsheet use default timings from constants
- **Parameters**: Advanced actions automatically receive appropriate parameters
- **Backwards Compatibility**: Legacy action names still work

## Installation

### On the Mini Pupper Robot

1. **Copy the enhanced files to the robot:**
   ```bash
   scp network_action_server.py ubuntu@10.0.0.10:/home/ubuntu/StanfordQuadruped/
   scp setup_enhanced_network_server.py ubuntu@10.0.0.10:/home/ubuntu/
   ```

2. **SSH to the robot and run setup:**
   ```bash
   ssh ubuntu@10.0.0.10
   cd /home/ubuntu
   sudo python3 setup_enhanced_network_server.py
   ```

3. **Verify the service is running:**
   ```bash
   sudo systemctl status quadruped-network-server
   curl http://localhost:8080/status
   ```

### On the PC Client

1. **Use the consolidated DogAction class:**
   ```python
   from actions.dog_action import DogAction
   ```

2. **Update the robot IP configuration:**
   ```python
   # In your robot configuration
   dog_action = DogAction(
       action_name_to_time=action_times,
       action_name_to_repeat_time=repeat_times,
       dog_id="dog_1",
       robot_ip="10.0.0.10",        # Robot's network IP
       robot_api_port=8080,         # API port (not UDP port)
   )
   ```

## API Reference

### Base URL
```
http://10.0.0.10:8080
```

### Endpoints

#### GET /status
Get current robot and queue status.

**Response:**
```json
{
  "running": true,
  "robot_state": {
    "activated": false,
    "walking_enabled": false,
    "dancing_enabled": false,
    "last_action": "move_forward",
    "last_action_time": "2024-01-01T12:00:00"
  },
  "queue_status": {
    "queue_size": 0,
    "current_action": null
  },
  "available_actions": ["move_forward", "move_backward", "look_up", ...]
}
```

#### GET /actions
List all available actions.

**Response:**
```json
{
  "available_actions": [
    "move_forward", "move_backward", "move_left", "move_right",
    "look_up", "look_down", "look_left", "look_right",
    "body_cycle", "head_ellipse", "rotate", "stop"
  ],
  "description": "Available MovementGroups actions for the dog robot"
}
```

#### POST /execute
Execute an action.

**Request:**
```json
{
  "action": "move_forward",
  "duration": 3.0,
  "parameters": {
    "v_x": 0.15,
    "v_y": 0.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Action 'move_forward' queued for execution",
  "action": "move_forward",
  "duration": 3.0,
  "parameters": {"v_x": 0.15, "v_y": 0.0}
}
```

#### POST /stop
Emergency stop all actions.

**Response:**
```json
{
  "success": true,
  "message": "Emergency stop executed"
}
```

#### POST /clear
Clear the action queue.

**Response:**
```json
{
  "success": true,
  "message": "Cleared 3 actions from queue",
  "cleared_count": 3
}
```

## Usage Examples

### Basic Usage
```python
from actions.dog_action import DogAction

# Create with MovementGroups action names
action_timings = {
    "move_forward": 3.0,
    "look_up": 2.0,
    "body_cycle": 5.0,
    "stop": 1.0,
}

dog = DogAction(
    action_name_to_time=action_timings,
    robot_ip="10.0.0.10",
    robot_api_port=8080
)

# Execute actions
dog.execute_action_sync("move_forward")
dog.execute_action_sync("look_up")
dog.execute_action_sync("body_cycle")
```

### Legacy Compatibility
```python
# Still works with old parameters
dog = DogAction(
    action_name_to_time=action_timings,
    robot_port=8830,  # Automatically converted to API port 8080
    dog_executor=None  # Ignored with warning
)
```

### Enhanced Features
```python
# Check robot status
status = dog.get_robot_status()
print(f"Connected: {status.get('connected')}")
print(f"Available actions: {status.get('available_actions')}")

# Emergency stop
dog.emergency_stop()

# Clear action queue
dog.clear_action_queue()

# Cleanup
dog.cleanup()
```

### Basic Movement Examples
```python
# Execute a simple forward movement
dog.execute_action_sync("move_forward")

# Execute with timing from spreadsheet
dog.execute_action_sync("look_up")

# Execute complex movements
dog.execute_action_sync("body_cycle")
dog.execute_action_sync("head_ellipse")
```

### Status Monitoring
```python
# Check robot status
status = dog.get_robot_status()
print(f"Robot connected: {status.get('connected', False)}")
print(f"Current action: {status.get('robot_state', {}).get('last_action')}")
print(f"Available actions: {status.get('available_actions', [])}")
```

### Emergency Control
```python
# Emergency stop
dog.emergency_stop()

# Clear action queue
dog.clear_action_queue()
```

### Advanced Integration
```python
# Use in existing choreography
def dance_sequence():
    actions = [
        "activate",
        "move_forward", 
        "look_up",
        "rotate",
        "body_cycle",
        "look_down",
        "stop"
    ]
    
    for action_name in actions:
        if not dog.execute_action_sync(action_name):
            print(f"Failed to execute {action_name}")
            break
        time.sleep(0.5)  # Brief pause between actions
```

## Migration from Old System

### Before (with complex mapping)
```python
# Had to use generic names that were mapped
action_timings = {
    "walk_forward": 3.0,    # Mapped to "forward"
    "look_up": 2.0,         # Mapped to "pitch_up"
    "dance_move": 5.0,      # Mapped to "dance"
}
```

### After (direct MovementGroups)
```python
# Use actual MovementGroups function names
action_timings = {
    "move_forward": 3.0,    # Direct MovementGroups function
    "look_up": 2.0,         # Direct MovementGroups function
    "body_cycle": 5.0,      # Direct MovementGroups function
}
```

## Network Configuration

### Robot Network Setup
The Mini Pupper should be configured with a static IP for reliable communication:

1. **Check current network configuration:**
   ```bash
   ip addr show
   ```

2. **The robot typically uses:**
   - IP: 10.0.0.10
   - Subnet: 10.0.0.0/24
   - Interface: Bridge (br0)

3. **PC network configuration:**
   - Connect to robot's WiFi network
   - Or ensure PC is on the same 10.0.0.0/24 network

### Firewall Configuration
Ensure the API port (8080) is accessible:

```bash
# On the robot
sudo ufw allow 8080/tcp
sudo ufw status
```

## Troubleshooting

### Common Issues

#### 1. Connection Failed
**Problem**: Cannot connect to robot at IP address
**Solutions**:
- Verify robot IP address is correct (usually 10.0.0.10)
- Check network connectivity: `ping 10.0.0.10`
- Ensure robot's network service is running
- Check firewall settings on robot

#### 2. Action Execution Failed
**Problem**: Actions are queued but not executing
**Solutions**:
- Check robot status: `GET /status`
- Verify action names are valid MovementGroups functions
- Check robot logs for errors
- Try emergency stop and clear queue

#### 3. API Port Issues
**Problem**: Cannot reach robot API
**Solutions**:
- Verify API port is 8080 (not UDP port 8830)
- Check if network service is running: `systemctl status quadruped-network-server`
- Restart the service: `sudo systemctl restart quadruped-network-server`

#### 4. Legacy Action Names
**Problem**: Old action names not working
**Solutions**:
- Update to use MovementGroups function names
- Check the valid actions list above
- Use backwards compatibility mappings when available

### Debug Commands

```bash
# Check robot network service
ssh ubuntu@10.0.0.10
sudo systemctl status quadruped-network-server
sudo journalctl -u quadruped-network-server -f

# Test API connectivity
curl http://10.0.0.10:8080/status
curl http://10.0.0.10:8080/actions

# Check network connectivity
ping 10.0.0.10
telnet 10.0.0.10 8080
```

### Log Files
- **PC Client**: Check `logs/dog_debug.log` for detailed connection and execution logs
- **Robot Server**: Check systemd journal for network service logs

## File Structure After Consolidation

```
actions/
├── dog_action.py              # Main enhanced class with all features
├── enhanced_dog_action.py     # Backwards compatibility aliases
├── base_action.py            # Base class (unchanged)
├── drone_action.py           # Drone actions (unchanged)
└── humanoid_action.py        # Humanoid actions (unchanged)

docs/
├── DOG_ACTION_CONSOLIDATION.md    # This comprehensive guide (consolidated from 3 docs)
├── CACHE_QUICK_START.md           # Caching system quick start
├── CACHING_OPTIMIZATION.md        # Caching optimization guide
└── FILE_ORGANIZATION.md           # Project file organization

StanfordQuadruped-mini_pupper/
├── network_action_server.py       # Robot-side API server
├── setup_enhanced_network_server.py  # Installation script
└── [other robot files]
```

## Benefits

1. **Simplified Architecture**: Single class instead of multiple separate classes
2. **Full Feature Set**: All advanced features in the main class
3. **Backwards Compatibility**: Existing code continues to work
4. **Direct MovementGroups Access**: No complex mapping logic
5. **Better Maintainability**: Single source of truth for dog actions
6. **Enhanced Error Handling**: Comprehensive network error management
7. **Real-time Monitoring**: Status and queue management capabilities
8. **Extensibility**: Easy addition of new MovementGroups functions

## Testing

Run the test script to verify all functionality:

```bash
python test_enhanced_dog_action.py
```

This will test all major MovementGroups actions and demonstrate the new direct integration.

## Migration Guide

### For New Code
```python
# Use the main DogAction class
from actions.dog_action import DogAction
```

### For Existing Code
```python
# Both import methods work for backwards compatibility:

# Option 1: Use the main consolidated class
from actions.dog_action import DogAction

# Option 2: Use the backwards compatibility import (still works)
from actions.enhanced_dog_action import NetworkDogAction
# NetworkDogAction is now an alias for DogAction

# Both create the same enhanced DogAction instance
dog1 = DogAction(action_name_to_time=action_timings)
dog2 = NetworkDogAction(action_name_to_time=action_timings)  # Same class!
```

### Updating Spreadsheet Actions
Update your Google Spreadsheet action cells to use the new MovementGroups function names:

**Old Names** → **New Names**:
- `walk_forward` → `move_forward`
- `walk_backward` → `move_backward`
- `turn_left` → `rotate` (with negative angle)
- `turn_right` → `rotate` (with positive angle)
- `pitch_up` → `look_up`
- `pitch_down` → `look_down`

## Conclusion

The consolidation provides a cleaner, more maintainable architecture with a single `DogAction` class that includes all enhanced functionality. The system now provides:

- **Direct MovementGroups Integration**: All functions accessible without mapping
- **Enhanced Network Communication**: Reliable HTTP API with proper error handling
- **Comprehensive Action Support**: Full range of movements from basic to complex
- **Full Backwards Compatibility**: All existing import methods continue to work
- **Real-time Monitoring**: Status and queue management
- **Easy Debugging**: Comprehensive logging and status reporting

The system maintains full backwards compatibility through alias imports, so existing code continues to work unchanged. All MovementGroups functions are now directly accessible without complex mapping logic.

**Note**: While `actions.enhanced_dog_action` still works for backwards compatibility, new code should prefer importing directly from `actions.dog_action` for clarity.
