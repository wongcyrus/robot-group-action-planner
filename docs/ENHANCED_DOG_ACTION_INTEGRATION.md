# Enhanced Dog Action Integration Documentation

## Overview

This document describes the enhanced dog action integration for the Stanford Quadruped Mini Pupper robot. The new architecture provides better network communication, improved error handling, and enhanced action management capabilities.

## Architecture

### Current Setup
```
PC (Robot Group Action Planner) <--HTTP API--> Mini Pupper Robot (Network Action Server) <--UDP--> Stanford Quadruped Control
```

### Components

1. **Network Action Server** (`network_action_server.py`)
   - Runs on the Mini Pupper robot
   - Provides RESTful HTTP API for remote control
   - Bridges HTTP requests to UDP commands
   - Manages action queuing and execution

2. **Enhanced Dog Action** (`enhanced_dog_action.py`)
   - Runs on the PC client
   - Replaces the original dog action implementation
   - Communicates with the robot via HTTP API
   - Provides backwards compatibility

3. **Setup Script** (`setup_enhanced_network_server.py`)
   - Installs and configures the network server on the robot
   - Creates systemd service for automatic startup
   - Provides easy deployment

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
- **Action name mapping** for compatibility with existing choreography

### 3. Improved Error Handling
- **Connection timeout** management
- **Graceful degradation** when robot is unreachable
- **Detailed logging** for debugging
- **Status feedback** for better monitoring

### 4. Backwards Compatibility
- **Drop-in replacement** for existing DogAction class
- **Same interface** for existing choreography scripts
- **Automatic parameter conversion** from legacy settings

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

1. **Replace the dog action import in your main script:**
   ```python
   # Old import
   # from actions.dog_action import DogAction
   
   # New import
   from actions.enhanced_dog_action import DogAction
   ```

2. **Update the robot IP configuration:**
   ```python
   # In your robot configuration
   dog_action = DogAction(
       action_name_to_time=action_times,
       action_name_to_repeat_time=repeat_times,
       dog_id="dog_1",
       robot_ip="10.0.0.10",  # Robot's network IP
       robot_port=8080,       # API port (not UDP port)
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
    "last_action": "forward",
    "last_action_time": "2024-01-01T12:00:00"
  },
  "queue_status": {
    "queue_size": 0,
    "current_action": null
  },
  "available_actions": ["forward", "backward", "left", "right", ...]
}
```

#### GET /actions
List all available actions.

**Response:**
```json
{
  "available_actions": [
    "forward", "backward", "left", "right", "turn_left", "turn_right",
    "activate", "deactivate", "trot", "hop", "dance", "stop",
    "pitch_up", "pitch_down", "height_up", "height_down", 
    "roll_left", "roll_right"
  ],
  "description": "Available actions for the dog robot"
}
```

#### POST /execute
Execute an action.

**Request:**
```json
{
  "action": "forward",
  "duration": 3.0,
  "parameters": {
    "ly": 0.8
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Action 'forward' queued for execution",
  "action": "forward",
  "duration": 3.0,
  "parameters": {"ly": 0.8}
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

## Action Mapping

The enhanced dog action provides automatic mapping from common action names to robot-specific commands:

| Original Action | Robot Command | Description |
|----------------|---------------|-------------|
| walk_forward | forward | Move forward |
| walk_backward | backward | Move backward |
| walk_left | left | Move left |
| walk_right | right | Move right |
| turn_left | turn_left | Rotate left |
| turn_right | turn_right | Rotate right |
| stand_up | activate | Activate/stand |
| sit_down | deactivate | Deactivate/sit |
| start_walking | trot | Enable walking mode |
| start_dance | dance | Enable dance mode |
| jump | hop | Jump/hop action |
| look_up | pitch_up | Pitch head up |
| look_down | pitch_down | Pitch head down |
| lean_left | roll_left | Roll body left |
| lean_right | roll_right | Roll body right |
| stand_tall | height_up | Increase height |
| crouch | height_down | Decrease height |

## Usage Examples

### Basic Movement
```python
# Execute a simple forward movement
dog_action.execute_action("walk_forward", duration=5.0)

# Execute with custom parameters
dog_action.execute_action("walk_forward", duration=3.0, parameters={"ly": 0.6})
```

### Status Monitoring
```python
# Check robot status
status = dog_action.get_robot_status()
print(f"Robot connected: {status.get('connected', False)}")
print(f"Current action: {status.get('robot_state', {}).get('last_action')}")
```

### Emergency Control
```python
# Emergency stop
dog_action.emergency_stop()

# Clear action queue
dog_action.clear_action_queue()
```

### Advanced Integration
```python
# Use in existing choreography
def dance_sequence():
    actions = [
        ("stand_up", 2.0),
        ("start_dance", 1.0),
        ("turn_left", 2.0),
        ("turn_right", 2.0),
        ("jump", 1.0),
        ("stop", 1.0)
    ]
    
    for action_name, duration in actions:
        if not dog_action._execute_single_action(action_name):
            print(f"Failed to execute {action_name}")
            break
        time.sleep(0.5)  # Brief pause between actions
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

### Connection Issues

1. **Check robot connectivity:**
   ```bash
   ping 10.0.0.10
   telnet 10.0.0.10 8080
   ```

2. **Check service status:**
   ```bash
   ssh ubuntu@10.0.0.10
   sudo systemctl status quadruped-network-server
   sudo journalctl -u quadruped-network-server -f
   ```

3. **Manual server start for debugging:**
   ```bash
   ssh ubuntu@10.0.0.10
   cd /home/ubuntu/StanfordQuadruped
   python3 network_action_server.py --host 0.0.0.0 --port 8080
   ```

### Action Execution Issues

1. **Check available actions:**
   ```bash
   curl http://10.0.0.10:8080/actions
   ```

2. **Monitor robot status:**
   ```bash
   curl http://10.0.0.10:8080/status
   ```

3. **Test manual action execution:**
   ```bash
   curl -X POST http://10.0.0.10:8080/execute \
        -H "Content-Type: application/json" \
        -d '{"action": "forward", "duration": 2.0}'
   ```

### Performance Issues

1. **Check network latency:**
   ```bash
   ping -c 10 10.0.0.10
   ```

2. **Monitor system resources on robot:**
   ```bash
   ssh ubuntu@10.0.0.10
   htop
   ```

3. **Adjust timeout settings:**
   ```python
   dog_action = DogAction(
       ...,
       connection_timeout=10.0,  # Increase for slow networks
       action_timeout=60.0       # Increase for long actions
   )
   ```

## Migration Guide

### From Original DogAction

1. **Update imports:**
   ```python
   # Before
   from actions.dog_action import DogAction
   
   # After
   from actions.enhanced_dog_action import DogAction
   ```

2. **Update initialization:**
   ```python
   # Before
   dog_action = DogAction(
       action_name_to_time=times,
       dog_executor=executor,
       robot_ip="127.0.0.1",
       robot_port=8830
   )
   
   # After
   dog_action = DogAction(
       action_name_to_time=times,
       robot_ip="10.0.0.10",
       robot_port=8080  # API port, not UDP port
   )
   ```

3. **Test existing choreography:**
   - Most existing code should work without changes
   - Action names are automatically mapped
   - Timing and repetition logic is preserved

### New Features to Leverage

1. **Use status monitoring:**
   ```python
   status = dog_action.get_robot_status()
   if status.get('connected'):
       # Execute actions
       pass
   else:
       print("Robot not reachable")
   ```

2. **Use emergency stop:**
   ```python
   try:
       # Execute complex choreography
       pass
   except KeyboardInterrupt:
       dog_action.emergency_stop()
   ```

3. **Use enhanced error handling:**
   ```python
   if not dog_action._execute_single_action("dance"):
       print("Dance action failed - robot may not be ready")
       dog_action.clear_action_queue()
   ```

## Future Enhancements

### Planned Features
- **WebSocket support** for real-time status streaming
- **Action recording and playback** for complex choreography
- **Multi-robot coordination** for group performances
- **Visual feedback integration** with camera feed
- **Voice command integration** via speech recognition

### Contributing
To contribute to the enhanced dog action system:

1. Test the current implementation thoroughly
2. Report issues with detailed logs
3. Suggest improvements for specific use cases
4. Help with documentation and examples

## Summary

The enhanced dog action integration provides a robust, network-based solution for controlling Stanford Quadruped Mini Pupper robots remotely. Key benefits include:

- ✅ **Reliable HTTP/REST API communication**
- ✅ **Better error handling and status monitoring**
- ✅ **Action queuing and management**
- ✅ **Backwards compatibility with existing code**
- ✅ **Easy deployment and service management**
- ✅ **Enhanced debugging and troubleshooting**

This solution addresses the limitations of the original UDP-based approach while maintaining compatibility with existing choreography and action definitions.
