# Enhanced Stanford Quadruped Integration

This repository provides a comprehensive integration system that bridges the **Enhanced Network Action Server** with the **Stanford Quadruped Mini Pupper** robot system, featuring improved choreography, network capabilities, and extensive action mapping.

## 🚀 Overview

The Enhanced Stanford Quadruped Integration combines:

- **Network-based Robot Control**: HTTP API for remote robot control
- **Advanced Choreography**: Enhanced dance sequences with improved flow and timing
- **Comprehensive Action Mapping**: 25+ actions across 7 categories
- **Backwards Compatibility**: Works with existing Stanford Quadruped systems
- **Real-time Monitoring**: Comprehensive logging and status monitoring
- **Multiple Control Methods**: Local, network, and API-based control

## 📁 Key Files

### Core Integration Files

```
enhanced_stanford_integration.py     # Main integration script
enhanced_action_mapping.py          # Action mapping system
StanfordQuadruped-mini_pupper/
└── src/
    └── createDanceActionListSample.py  # Enhanced choreography
```

### Network Components

```
network_action_server.py            # HTTP API server (runs on robot)
enhanced_dog_action.py              # Network client (runs on PC)
dog_action.py                       # Backwards compatible wrapper
```

### Deployment and Setup

```
setup_enhanced_network_server.py    # Robot setup automation
deploy_enhanced_dog_action.py       # PC deployment automation
```

## 🔧 Installation & Setup

### 1. Robot Setup (Stanford Quadruped Mini Pupper)

```bash
# On the robot (Mini Pupper)
cd /home/ubuntu/robot-action-planner
python setup_enhanced_network_server.py
```

This will:
- Install the enhanced network action server
- Configure automatic startup
- Set up the HTTP API on port 8080
- Configure logging and monitoring

### 2. PC Setup (Control Computer)

```bash
# On your PC
python deploy_enhanced_dog_action.py --target-ip 10.0.0.10
```

This will:
- Deploy the enhanced dog action client
- Configure network connectivity
- Set up the action mapping system
- Test the connection

### 3. Enhanced Choreography Setup

The enhanced choreography is automatically available in:
```
StanfordQuadruped-mini_pupper/src/createDanceActionListSample.py
```

## 🎭 Enhanced Choreography Features

### Improved Action Sequences

The enhanced choreography includes:

1. **Greeting Sequence**: Multi-directional acknowledgment
2. **Warm-up Movements**: Gentle preparation motions
3. **10 Main Patterns**: Comprehensive movement combinations
4. **Advanced Choreography**: Level 3 complex movements
5. **Grand Finale**: Dramatic conclusion with audience engagement

### Movement Categories

- **Directional Flow**: Forward, backward, left, right movements
- **Diagonal Dynamics**: Complex directional combinations
- **Head Choreography**: Expressive head movements
- **Body Expression**: Tilting and rolling motions
- **Gait Variations**: Speed and direction combinations
- **Leg Articulation**: Individual leg movements
- **Height Dynamics**: Vertical positioning changes
- **Rotational Elements**: Turning and spinning
- **Advanced Combinations**: Simultaneous multi-axis movements
- **Complex Patterns**: Level 3 API utilization

## 🌐 Network API Usage

### Starting the Network Server

```bash
# On the robot
python enhanced_stanford_integration.py --network-mode --port 8080
```

### API Endpoints

#### Execute Action
```bash
curl -X POST http://10.0.0.10:8080/execute \
     -H "Content-Type: application/json" \
     -d '{
       "action": "dance",
       "parameters": {
         "duration": 15.0,
         "intensity": 1.2,
         "speed": 1.0
       }
     }'
```

#### Get Status
```bash
curl http://10.0.0.10:8080/status
```

### Available Actions

#### Basic Movement (7 actions)
- `forward`, `backward`, `left`, `right`
- `turn_left`, `turn_right`, `stop`

#### Activation & Control (3 actions)
- `activate`, `deactivate`, `emergency_stop`

#### Entertainment (4 actions)
- `dance`, `bow`, `wave`, `celebrate`

#### Posture & Attitude (6 actions)
- `pitch_up`, `pitch_down`, `roll_left`, `roll_right`
- `height_up`, `height_down`

#### Head Movement (4 actions)
- `look_up`, `look_down`, `look_left`, `look_right`

#### Advanced Movement (4 actions)
- `circle`, `figure_eight`, `shake`, `stretch`

#### Complex Choreography (3 actions)
- `complex_dance`, `greeting_sequence`, `finale_sequence`

## 🎯 Usage Examples

### 1. Run Enhanced Choreography

```bash
# Local execution
python enhanced_stanford_integration.py --choreography

# Network execution
curl -X POST http://10.0.0.10:8080/execute \
     -H "Content-Type: application/json" \
     -d '{"action": "complex_dance", "parameters": {"duration": 30.0}}'
```

### 2. Demo Mode

```bash
python enhanced_stanford_integration.py --demo-mode
```

### 3. Specific Action Execution

```bash
# Command line
python enhanced_stanford_integration.py --action dance --duration 10.0 --intensity 1.5

# Network API
curl -X POST http://10.0.0.10:8080/execute \
     -H "Content-Type: application/json" \
     -d '{
       "action": "greeting_sequence",
       "parameters": {"duration": 5.0}
     }'
```

### 4. List Available Actions

```bash
python enhanced_stanford_integration.py --list-actions
```

## 🔄 Action Parameters

All actions support these parameters:

- **duration** (float): Action duration in seconds (0.1-10.0)
- **intensity** (float): Action intensity multiplier (0.1-2.0)
- **speed** (float): Action speed multiplier (0.1-2.0)
- **direction** (string): Direction parameter where applicable

### Parameter Examples

```json
{
  "action": "dance",
  "parameters": {
    "duration": 15.0,    // 15 second dance
    "intensity": 1.3,    // 30% more intense movements
    "speed": 0.8         // 20% slower execution
  }
}
```

## 📊 Monitoring & Logging

### Log Files

```
logs/
├── enhanced_stanford_integration.log    # Main integration log
├── robot_planner.log                   # General system log
├── dog_debug.log                       # Dog action debug log
└── network_action_server.log           # Network server log
```

### Real-time Monitoring

```bash
# Monitor integration log
tail -f logs/enhanced_stanford_integration.log

# Monitor network server
tail -f logs/network_action_server.log
```

## 🔧 Configuration

### Network Configuration

Default settings:
- **Robot IP**: `10.0.0.10`
- **HTTP Port**: `8080`
- **UDP Port**: `8830` (Stanford Quadruped)

### Modify IP Settings

```bash
# Change robot IP
python enhanced_stanford_integration.py --robot-ip 192.168.1.100 --network-mode

# Change HTTP port
python enhanced_stanford_integration.py --port 8081 --network-mode
```

## 🚨 Emergency Procedures

### Emergency Stop

```bash
# Command line
python enhanced_stanford_integration.py --action emergency_stop

# Network API
curl -X POST http://10.0.0.10:8080/execute \
     -H "Content-Type: application/json" \
     -d '{"action": "emergency_stop"}'
```

### Recovery Procedures

1. **Connection Issues**: Check network connectivity and firewall settings
2. **Movement Problems**: Execute `emergency_stop` followed by `activate`
3. **Server Issues**: Restart the network server on the robot
4. **Choreography Errors**: Check logs for specific error messages

## 🔍 Troubleshooting

### Common Issues

1. **"MovementGroups not available"**
   - Ensure you're running on the Stanford Quadruped system
   - Check that the `src` directory is properly configured

2. **Network Connection Failed**
   - Verify robot IP address: `ping 10.0.0.10`
   - Check if network server is running: `curl http://10.0.0.10:8080/status`
   - Verify firewall settings allow port 8080

3. **Action Execution Failed**
   - Check available actions: `--list-actions`
   - Verify action parameters are within valid ranges
   - Check logs for specific error messages

### Debug Mode

```bash
python enhanced_stanford_integration.py --log-level DEBUG --action dance
```

## 🚀 Advanced Usage

### Custom Choreography

Create custom choreography by modifying `createDanceActionListSample.py`:

```python
from src.MovementGroup import MovementGroups

Move = MovementGroups()

# Your custom choreography
Move.look_up()
Move.dance_move_custom()
Move.finale_bow()

MovementLib = Move.MovementLib
```

### Network Integration with Existing Systems

```python
import requests

# Execute action from your application
response = requests.post('http://10.0.0.10:8080/execute', 
                        json={
                            'action': 'dance',
                            'parameters': {'duration': 10.0}
                        })
```

## 📝 Development

### Adding New Actions

1. Add action mapping in `enhanced_action_mapping.py`:
```python
def _execute_my_action(self, params: ActionParameters) -> None:
    """Execute my custom action"""
    # Implementation here
    pass
```

2. Add to action map:
```python
"my_action": self._execute_my_action,
```

### Testing

```bash
# Test specific functionality
python enhanced_stanford_integration.py --action my_action --duration 2.0
```

## 📚 Documentation Structure

```
docs/
├── ENHANCED_CHOREOGRAPHY.md         # Choreography documentation
├── NETWORK_API_REFERENCE.md         # API endpoint reference
├── ACTION_MAPPING_GUIDE.md          # Action mapping guide
├── DEPLOYMENT_GUIDE.md              # Deployment procedures
└── TROUBLESHOOTING_GUIDE.md         # Detailed troubleshooting
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Test with the robot system
5. Submit a pull request

## 📄 License

Apache License 2.0 - see LICENSE file for details.

## 🙏 Acknowledgments

- **Stanford Quadruped Team**: Original MovementGroups API
- **MangDang**: Mini Pupper hardware platform
- **Robot Action Planner**: Enhanced integration framework

---

**Note**: This enhanced integration maintains full backwards compatibility with existing Stanford Quadruped systems while providing significant improvements in network capabilities, choreography, and action management.
