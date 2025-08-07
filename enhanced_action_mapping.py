"""
Enhanced Action Mapping for Stanford Quadruped Integration
=========================================================

This module provides mapping between the enhanced network action server commands
and the Stanford Quadruped MovementGroups API for seamless integration.

The mapping allows the enhanced dog action system to utilize the full range
of Stanford Quadruped movements while maintaining network API compatibility.

Author: Enhanced Robot Action Planner System
Date: 2024
License: Apache 2.0
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ActionParameters:
    """Data class for action parameters with validation"""

    duration: float = 1.0
    intensity: float = 1.0
    speed: float = 1.0
    direction: str = "forward"

    def __post_init__(self):
        """Validate parameters after initialization"""
        self.duration = max(0.1, min(10.0, self.duration))
        self.intensity = max(0.1, min(2.0, self.intensity))
        self.speed = max(0.1, min(2.0, self.speed))


class EnhancedActionMapper:
    """
    Maps enhanced network action commands to Stanford Quadruped movements

    This class provides a bridge between the HTTP API actions and the
    underlying Stanford Quadruped MovementGroups system.
    """

    def __init__(self, movement_groups):
        """
        Initialize the action mapper

        Args:
            movement_groups: Stanford Quadruped MovementGroups instance
        """
        self.move = movement_groups
        self.logger = logging.getLogger(__name__)

        # Initialize action mapping dictionary
        self._init_action_mappings()

    def _init_action_mappings(self) -> None:
        """Initialize the action mapping dictionary"""
        self.action_map: Dict[str, Callable] = {
            # Basic Movement Actions
            "forward": self._execute_forward,
            "backward": self._execute_backward,
            "left": self._execute_left,
            "right": self._execute_right,
            "turn_left": self._execute_turn_left,
            "turn_right": self._execute_turn_right,
            "stop": self._execute_stop,
            # Activation and Control
            "activate": self._execute_activate,
            "deactivate": self._execute_deactivate,
            "emergency_stop": self._execute_emergency_stop,
            # Dance and Entertainment
            "dance": self._execute_dance,
            "bow": self._execute_bow,
            "wave": self._execute_wave,
            "celebrate": self._execute_celebrate,
            # Attitude and Posture
            "pitch_up": self._execute_pitch_up,
            "pitch_down": self._execute_pitch_down,
            "roll_left": self._execute_roll_left,
            "roll_right": self._execute_roll_right,
            "height_up": self._execute_height_up,
            "height_down": self._execute_height_down,
            # Head Movements
            "look_up": self._execute_look_up,
            "look_down": self._execute_look_down,
            "look_left": self._execute_look_left,
            "look_right": self._execute_look_right,
            # Advanced Movements
            "circle": self._execute_circle,
            "figure_eight": self._execute_figure_eight,
            "shake": self._execute_shake,
            "stretch": self._execute_stretch,
            # Complex Choreography
            "complex_dance": self._execute_complex_dance,
            "greeting_sequence": self._execute_greeting_sequence,
            "finale_sequence": self._execute_finale_sequence,
        }

    def execute_action(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute a mapped action with optional parameters

        Args:
            action: Action name to execute
            parameters: Optional parameters for the action

        Returns:
            bool: True if action executed successfully, False otherwise
        """
        try:
            # Create ActionParameters object
            if parameters is None:
                parameters = {}
            action_params = ActionParameters(**parameters)

            # Get the action function
            action_func = self.action_map.get(action.lower())
            if action_func is None:
                self.logger.error(f"Unknown action: {action}")
                return False

            # Execute the action
            self.logger.info(f"Executing action: {action} with params: {parameters}")
            action_func(action_params)
            return True

        except Exception as e:
            self.logger.error(f"Error executing action {action}: {str(e)}")
            return False

    def get_available_actions(self) -> list:
        """Get list of available actions"""
        return list(self.action_map.keys())

    # === BASIC MOVEMENT IMPLEMENTATIONS ===

    def _execute_forward(self, params: ActionParameters) -> None:
        """Execute forward movement"""
        speed = 0.2 * params.speed
        duration = params.duration
        self.move.gait_uni(speed, 0, duration, 0.5)

    def _execute_backward(self, params: ActionParameters) -> None:
        """Execute backward movement"""
        speed = -0.2 * params.speed
        duration = params.duration
        self.move.gait_uni(speed, 0, duration, 0.5)

    def _execute_left(self, params: ActionParameters) -> None:
        """Execute left movement"""
        speed = 0.15 * params.speed
        duration = params.duration
        self.move.gait_uni(0, -speed, duration, 0.5)

    def _execute_right(self, params: ActionParameters) -> None:
        """Execute right movement"""
        speed = 0.15 * params.speed
        duration = params.duration
        self.move.gait_uni(0, speed, duration, 0.5)

    def _execute_turn_left(self, params: ActionParameters) -> None:
        """Execute left turn"""
        angle = -45 * params.intensity
        self.move.rotate(angle)
        self.move.stop(0.5)

    def _execute_turn_right(self, params: ActionParameters) -> None:
        """Execute right turn"""
        angle = 45 * params.intensity
        self.move.rotate(angle)
        self.move.stop(0.5)

    def _execute_stop(self, params: ActionParameters) -> None:
        """Execute stop"""
        self.move.stop(params.duration)

    # === ACTIVATION AND CONTROL ===

    def _execute_activate(self, params: ActionParameters) -> None:
        """Execute activation sequence"""
        self.move.look_up()
        self.move.height_move(0.02, 1, 0.5)
        self.move.stop(0.5)

    def _execute_deactivate(self, params: ActionParameters) -> None:
        """Execute deactivation sequence"""
        self.move.height_move(-0.01, 1, 0.5)
        self.move.look_down()
        self.move.stop(1)

    def _execute_emergency_stop(self, params: ActionParameters) -> None:
        """Execute emergency stop"""
        self.move.stop(0.1)
        self.move.height_move(-0.02, 0.5, 0.2)
        self.move.stop(2)

    # === DANCE AND ENTERTAINMENT ===

    def _execute_dance(self, params: ActionParameters) -> None:
        """Execute dance sequence"""
        duration_scale = params.duration / 10.0  # Scale for total duration

        # Basic dance moves
        self.move.look_right()
        self.move.look_left()
        self.move.body_row(10 * params.intensity, 1 * duration_scale, 0.5)
        self.move.body_row(-10 * params.intensity, 1 * duration_scale, 0.5)
        self.move.height_move(0.02 * params.intensity, 1 * duration_scale, 0.5)
        self.move.height_move(-0.01 * params.intensity, 1 * duration_scale, 0.5)
        self.move.rotate(360)
        self.move.stop(0.5)

    def _execute_bow(self, params: ActionParameters) -> None:
        """Execute bow sequence"""
        angle = 15 * params.intensity
        self.move.bowback(angle)
        self.move.stop(params.duration)

    def _execute_wave(self, params: ActionParameters) -> None:
        """Execute wave sequence"""
        for _ in range(int(2 * params.intensity)):
            self.move.foreleg_lift("right", 0.03, 0.8, 0.3)
            self.move.foreleg_lift("left", 0.03, 0.8, 0.3)
        self.move.stop(0.5)

    def _execute_celebrate(self, params: ActionParameters) -> None:
        """Execute celebration sequence"""
        self.move.height_move(0.03 * params.intensity, 1, 0.5)
        self.move.head_move(20, 0, 1, 0.5)
        for _ in range(3):
            self.move.body_row(8, 0.5, 0.3)
            self.move.body_row(-8, 0.5, 0.3)
        self.move.height_move(0, 1, 0.5)
        self.move.head_move(0, 0, 1, 0.5)

    # === ATTITUDE AND POSTURE ===

    def _execute_pitch_up(self, params: ActionParameters) -> None:
        """Execute pitch up"""
        angle = 15 * params.intensity
        self.move.head_move(angle, 0, params.duration, 0.5)

    def _execute_pitch_down(self, params: ActionParameters) -> None:
        """Execute pitch down"""
        angle = -15 * params.intensity
        self.move.head_move(angle, 0, params.duration, 0.5)

    def _execute_roll_left(self, params: ActionParameters) -> None:
        """Execute roll left"""
        angle = -10 * params.intensity
        self.move.body_row(angle, params.duration, 0.5)

    def _execute_roll_right(self, params: ActionParameters) -> None:
        """Execute roll right"""
        angle = 10 * params.intensity
        self.move.body_row(angle, params.duration, 0.5)

    def _execute_height_up(self, params: ActionParameters) -> None:
        """Execute height increase"""
        height = 0.02 * params.intensity
        self.move.height_move(height, params.duration, 0.5)

    def _execute_height_down(self, params: ActionParameters) -> None:
        """Execute height decrease"""
        height = -0.02 * params.intensity
        self.move.height_move(height, params.duration, 0.5)

    # === HEAD MOVEMENTS ===

    def _execute_look_up(self, params: ActionParameters) -> None:
        """Execute look up"""
        self.move.look_up()
        self.move.stop(params.duration)

    def _execute_look_down(self, params: ActionParameters) -> None:
        """Execute look down"""
        self.move.look_down()
        self.move.stop(params.duration)

    def _execute_look_left(self, params: ActionParameters) -> None:
        """Execute look left"""
        self.move.look_left()
        self.move.stop(params.duration)

    def _execute_look_right(self, params: ActionParameters) -> None:
        """Execute look right"""
        self.move.look_right()
        self.move.stop(params.duration)

    # === ADVANCED MOVEMENTS ===

    def _execute_circle(self, params: ActionParameters) -> None:
        """Execute circular movement"""
        radius = 0.15 * params.intensity
        steps = 8
        angle_step = 360 / steps

        for i in range(steps):
            self.move.rotate(angle_step)
            self.move.gait_uni(radius, 0, 0.5, 0.3)
        self.move.stop(0.5)

    def _execute_figure_eight(self, params: ActionParameters) -> None:
        """Execute figure-eight movement"""
        # First loop
        for i in range(4):
            self.move.rotate(90)
            self.move.gait_uni(0.1 * params.speed, 0.1 * params.speed, 0.8, 0.4)

        # Second loop (opposite direction)
        for i in range(4):
            self.move.rotate(-90)
            self.move.gait_uni(0.1 * params.speed, -0.1 * params.speed, 0.8, 0.4)

        self.move.stop(0.5)

    def _execute_shake(self, params: ActionParameters) -> None:
        """Execute shake movement"""
        intensity = params.intensity
        for _ in range(int(4 * intensity)):
            self.move.body_row(5 * intensity, 0.2, 0.1)
            self.move.body_row(-5 * intensity, 0.2, 0.1)
        self.move.body_row(0, 0.5, 0.3)

    def _execute_stretch(self, params: ActionParameters) -> None:
        """Execute stretch sequence"""
        # Forward stretch
        self.move.height_move(0.03 * params.intensity, 1.5, 0.8)
        self.move.gait_uni(0.1, 0, 2, 1)

        # Backward stretch
        self.move.gait_uni(-0.1, 0, 2, 1)
        self.move.height_move(0, 1, 0.5)
        self.move.stop(0.5)

    # === COMPLEX CHOREOGRAPHY ===

    def _execute_complex_dance(self, params: ActionParameters) -> None:
        """Execute complex dance choreography"""
        # Use the Level 3 complex movements
        self.move.body_cycle()
        self.move.head_ellipse()

        # Add custom complex sequence
        self.move.gait_uni(0.2, 0.1, 2, 0.8)
        self.move.rotate(180)
        self.move.gait_uni(-0.15, -0.1, 2, 0.8)
        self.move.rotate(180)
        self.move.stop(1)

    def _execute_greeting_sequence(self, params: ActionParameters) -> None:
        """Execute greeting sequence"""
        # Look around greeting
        self.move.look_up()
        self.move.look_right()
        self.move.look_upperright()
        self.move.look_left()
        self.move.look_upperleft()
        self.move.look_down()

        # Gentle nod
        self.move.head_move(15, 0, 1, 0.5)
        self.move.head_move(0, 0, 1, 0.5)
        self.move.stop(0.5)

    def _execute_finale_sequence(self, params: ActionParameters) -> None:
        """Execute finale sequence"""
        # Grand finale
        self.move.height_move(0.035, 1.5, 1)
        self.move.head_move(25, 0, 2, 1)
        self.move.stop(2)

        # Graceful descent
        self.move.height_move(-0.02, 2, 1.5)
        self.move.head_move(-15, 0, 1.5, 1)
        self.move.stop(1.5)

        # Return to neutral
        self.move.head_move(0, 0, 1, 0.8)
        self.move.height_move(0, 1, 0.8)
        self.move.stop(2)


def create_action_mapper(movement_groups) -> EnhancedActionMapper:
    """
    Factory function to create an enhanced action mapper

    Args:
        movement_groups: Stanford Quadruped MovementGroups instance

    Returns:
        EnhancedActionMapper: Configured action mapper instance
    """
    return EnhancedActionMapper(movement_groups)


# Example usage and testing
if __name__ == "__main__":
    # This would be used with actual MovementGroups in the Stanford Quadruped environment
    print("Enhanced Action Mapping System")
    print("=============================")

    # Create a mock MovementGroups for testing
    class MockMovementGroups:
        def __init__(self):
            self.MovementLib = []

        def __getattr__(self, name):
            return lambda *args, **kwargs: print(f"Mock: {name}({args}, {kwargs})")

    # Test the mapper
    mock_move = MockMovementGroups()
    mapper = create_action_mapper(mock_move)

    print(f"Available actions: {len(mapper.get_available_actions())}")
    print("Action categories:")
    actions = mapper.get_available_actions()

    # Group actions by category
    categories = {
        "Basic Movement": [
            a
            for a in actions
            if a
            in [
                "forward",
                "backward",
                "left",
                "right",
                "turn_left",
                "turn_right",
                "stop",
            ]
        ],
        "Activation": [
            a for a in actions if a in ["activate", "deactivate", "emergency_stop"]
        ],
        "Entertainment": [
            a for a in actions if a in ["dance", "bow", "wave", "celebrate"]
        ],
        "Posture": [
            a
            for a in actions
            if a
            in [
                "pitch_up",
                "pitch_down",
                "roll_left",
                "roll_right",
                "height_up",
                "height_down",
            ]
        ],
        "Head Movement": [
            a
            for a in actions
            if a in ["look_up", "look_down", "look_left", "look_right"]
        ],
        "Advanced": [
            a for a in actions if a in ["circle", "figure_eight", "shake", "stretch"]
        ],
        "Complex": [
            a
            for a in actions
            if a in ["complex_dance", "greeting_sequence", "finale_sequence"]
        ],
    }

    for category, cat_actions in categories.items():
        print(f"  {category}: {len(cat_actions)} actions")

    print("\nTesting sample action execution...")

    # Test some actions
    test_params = {"duration": 2.0, "intensity": 1.5, "speed": 1.2}
    mapper.execute_action("dance", test_params)
    mapper.execute_action("greeting_sequence")
    mapper.execute_action("forward", {"speed": 0.8, "duration": 1.5})

    print("Enhanced Action Mapping System ready for integration!")
