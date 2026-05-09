# Action timing constants for robot-group-action-planner
# This file contains default action timings for different robot types

# Default action timings for different robot types
# These values are extracted from the action classes to centralize timing configuration

# Dog robot default action timings (seconds)
# Updated to match actual MovementGroups methods and their timing behavior
DOG_DEFAULT_ACTION_TIMES = {
    # Stop action - respects duration parameter
    "stop": 2.0,
    # Basic movement actions - use fixed internal timing (~70 iterations * 0.015s = ~1.05s)
    "move_forward": 1.1,
    "move_backward": 1.1,
    "move_left": 1.1,
    "move_right": 1.1,
    "move_leftfront": 1.1,
    "move_rightfront": 1.1,
    "move_leftback": 1.1,
    "move_rightback": 1.1,
    # Head movement actions - simple versions use fixed timing
    "look_up": 1.0,
    "look_down": 1.0,
    "look_left": 1.0,
    "look_right": 1.0,
    "look_upperleft": 1.0,
    "look_upperright": 1.0,
    "look_rightlower": 1.0,
    "look_leftlower": 1.0,
    # Parametric movement actions - respect time_uni and time_acc parameters
    "head_move": 3.0,  # Uses time_uni parameter for duration
    "gait_uni": 3.0,  # Uses time_uni parameter for uniform movement
    "height_move": 2.0,  # Uses time_uni parameter for holding position
    "body_row": 2.0,  # Uses time_uni parameter for duration
    # Leg lift actions - respect time_uni and time_acc parameters
    "foreleg_lift": 2.0,  # Uses time_uni parameter for holding lifted position
    "backleg_lift": 2.0,  # Uses time_uni parameter for holding lifted position
    # Rotation actions - calculate duration based on angle parameter
    "rotate": 3.0,  # Duration calculated from angle/0.66 * 0.015s per iteration
    "bowback": 3.0,  # Fixed 20 iterations * 0.015s = 0.3s movement + attitude hold
    # Complex movement examples (Level 3 API)
    "body_cycle": 5.0,  # Complex circular body movement
}

# Drone robot default action timings (seconds)
DRONE_DEFAULT_ACTION_TIMES = {
    # Takeoff and landing
    "takeoff": 3.0,
    "land": 3.0,
    # Movement actions (with common parameter variations)
    "move_up": 2.0,
    "move_up_20": 2.0,
    "move_up_50": 2.0,
    "move_up_100": 2.0,
    "move_down": 2.0,
    "move_down_20": 2.0,
    "move_down_50": 2.0,
    "move_down_100": 2.0,
    "move_left": 2.0,
    "move_left_20": 2.0,
    "move_left_50": 2.0,
    "move_left_100": 2.0,
    "move_right": 2.0,
    "move_right_20": 2.0,
    "move_right_50": 2.0,
    "move_right_100": 2.0,
    "move_forward": 2.0,
    "move_forward_20": 2.0,
    "move_forward_50": 2.0,
    "move_forward_100": 2.0,
    "move_back": 2.0,
    "move_back_20": 2.0,
    "move_back_50": 2.0,
    "move_back_100": 2.0,
    # Rotation actions
    "rotate_cw": 3.0,
    "rotate_cw_90": 3.0,
    "rotate_cw_180": 3.0,
    "rotate_ccw": 3.0,
    "rotate_ccw_90": 3.0,
    "rotate_ccw_180": 3.0,
    # Flip actions
    "flip_forward": 4.0,
    "flip_back": 4.0,
    "flip_left": 4.0,
    "flip_right": 4.0,
    # Special actions
    "hover": 4.0,
    # Complex movement actions
    "curve": 7.0,
    "go": 3.0,
    "jump": 5.0,
}

# Drone action pattern fallback timings (for actions that match patterns but aren't in the main dict)
DRONE_PATTERN_FALLBACK_TIMES = {
    "takeoff": 3.0,
    "land": 3.0,
    "hover": 4.0,
    "curve": 7.0,  # Complex curve movements
    "go": 3.0,  # XYZ movement actions
    "jump": 5.0,  # Jump actions
    "move": 2.0,  # Base movement pattern
    "rotate": 3.0,  # Base rotation pattern
    "flip": 4.0,  # Base flip pattern
}

# Dog action pattern fallback timings (for actions that match patterns but aren't in the main dict)
# Updated to match actual MovementGroups patterns and timing behavior
DOG_PATTERN_FALLBACK_TIMES = {
    # Movement patterns
    "move": 1.1,  # Base pattern for move_* actions (fixed timing)
    "look": 1.0,  # Base pattern for look_* actions (fixed timing)
    # Parametric action patterns
    "gait": 3.0,  # Pattern for gait_* actions (parametric timing)
    "head": 3.0,  # Pattern for head_* actions (parametric timing)
    "body": 2.0,  # Pattern for body_* actions (parametric timing)
    "height": 2.0,  # Pattern for height_* actions (parametric timing)
    "foreleg": 2.0,  # Pattern for foreleg_* actions (parametric timing)
    "backleg": 2.0,  # Pattern for backleg_* actions (parametric timing)
    # Special actions
    "stop": 2.0,  # Stop action
    "rotate": 3.0,  # Rotation actions
    "bowback": 3.0,  # Bow back action
    # Legacy fallbacks for old action names (if any still exist in spreadsheets)
    "forward": 1.1,  # Mapped to move_forward
    "backward": 1.1,  # Mapped to move_backward
    "left": 1.1,  # Mapped to move_left
    "right": 1.1,  # Mapped to move_right
}
