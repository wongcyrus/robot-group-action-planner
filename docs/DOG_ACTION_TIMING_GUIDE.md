# Dog Action Timing Guide

This document explains how action durations work in the dog robot system, from the action planner through to the MovementGroups execution.

## Action Flow

```
DogAction → network_action_server.py → MovementGroups → MovementScheme
```

## Duration Parameter Behavior

The MovementGroups actions fall into three categories regarding duration handling:

### 1. Fixed Duration Actions (Level 1 API)

These actions ignore the external duration parameter and use fixed internal timing:

**Simple Movement Actions** (~1.1 seconds):
- `move_forward()`, `move_backward()`, `move_left()`, `move_right()`
- `move_leftfront()`, `move_rightfront()`, `move_leftback()`, `move_rightback()`
- Duration: ~70 iterations × 0.015s = ~1.05 seconds

**Simple Look Actions** (~1.0 seconds):
- `look_up()`, `look_down()`, `look_left()`, `look_right()`
- `look_upperleft()`, `look_upperright()`, `look_rightlower()`, `look_leftlower()`
- Duration: ~67 iterations × 0.015s = ~1.0 seconds

### 2. Parametric Duration Actions (Level 2 API)

These actions respect the `time_uni` and `time_acc` parameters passed from the network server:

**Head Movement**:
- `head_move(pitch_deg, yaw_deg, time_uni, time_acc)`
- `time_uni`: How long to hold the position (maps to duration)
- `time_acc`: How long to transition to the position

**Body Movement**:
- `gait_uni(v_x, v_y, time_uni, time_acc)` - Uniform gait movement
- `height_move(ht, time_uni, time_acc)` - Height adjustment
- `body_row(row_deg, time_uni, time_acc)` - Body roll movement

**Leg Movement**:
- `foreleg_lift(leg_index, ht, time_uni, time_acc)` - Front leg lift
- `backleg_lift(leg_index, ht, time_uni, time_acc)` - Back leg lift

### 3. Special Duration Actions

**Stop Action**:
- `stop(time)` - Directly uses the time parameter
- Duration: Exactly as specified

**Rotation Action**:
- `rotate(angle)` - Duration calculated from angle
- Formula: `number = abs(angle) / 0.66`
- Duration: `number × 0.015s` per iteration

**Bow Back Action**:
- `bowback(angle)` - Fixed movement duration with attitude hold
- Movement: 20 iterations × 0.015s = 0.3s
- Plus attitude holding time

## Network Server Parameter Mapping

The `network_action_server.py` maps the duration parameter to MovementGroups parameters:

```python
# For parametric actions
time_uni = parameters.get("time_uni", duration)  # Main duration
time_acc = parameters.get("time_acc", duration * 0.3)  # Acceleration time

# For stop action
movement_func(time=duration)

# For rotation
angle = parameters.get("angle", 30)  # Default 30 degrees
movement_func(angle=angle)
```

## Updated DOG_DEFAULT_ACTION_TIMES

The `constant.py` file has been updated with accurate timing values:

- **Fixed duration actions**: Set to actual measured durations
- **Parametric actions**: Set to reasonable defaults for `time_uni`
- **Special actions**: Set based on typical usage patterns

## Recommendations

1. **For choreography**: Use parametric actions (`head_move`, `gait_uni`, etc.) when precise timing is needed
2. **For simple movements**: Use Level 1 API actions for consistent, predictable timing
3. **For complex sequences**: Consider the actual execution time vs. the requested duration
4. **For spreadsheet planning**: Use the updated timing values in `DOG_DEFAULT_ACTION_TIMES`

## Debugging Timing Issues

1. Check the MovementGroups method signature to see if it accepts timing parameters
2. Verify that the network server maps duration correctly to the method parameters
3. Test actual execution time vs. expected duration
4. Consider the difference between movement time and hold time for parametric actions

## Movement Scheme Timing

All MovementGroups use a base timing interval:
- `dt = 0.015` seconds per iteration
- `InterpolationNumber = 70` (default for most actions)
- This gives ~1.05 seconds for standard fixed-duration movements

The `MovementScheme` class handles the interpolation between movement points and maintains the timing loop at 15ms intervals.
