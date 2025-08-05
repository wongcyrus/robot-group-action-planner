import logging
from typing import Any, Dict, List, Union

from jinja2 import BaseLoader, Environment

from spreadsheet_loader import SpreadsheetLoader
from constant import (
    DOG_DEFAULT_ACTION_TIMES,
    DRONE_DEFAULT_ACTION_TIMES,
    DOG_PATTERN_FALLBACK_TIMES,
    DRONE_PATTERN_FALLBACK_TIMES
)


class ActionCompiler:
    """
    Compiles and validates robot action sequences from spreadsheet data.

    This class is responsible for:
    1. Compiling action sequences from spreadsheet data
    2. Validating that all actions exist in the action details
    3. Ensuring that action execution times don't exceed allotted time slots
    """

    def __init__(self, spreadsheet_loader: SpreadsheetLoader):
        """
        Initialize the ActionCompiler with a SpreadsheetLoader.

        Args:
            spreadsheet_loader: A loader that provides access to spreadsheet data
        """
        self.spreadsheet_loader = spreadsheet_loader
        self.logger = logging.getLogger("ActionCompiler")

    def _get_robot_keys(self, action: Dict[str, str]) -> List[str]:
        """Helper to get all robot keys in an action row.
        
        Returns keys that start with:
        - Humanoid_ (humanoid robots)
        - Drone_ (drone robots)  
        - Dog_ (dog robots)
        """
        return [key for key in action if key.startswith(( "Humanoid_", "Drone_", "Dog_"))]

    def _get_dog_default_actions(self) -> Dict[str, float]:
        """Extract default dog action timings from constants."""
        return DOG_DEFAULT_ACTION_TIMES.copy()

    def _get_drone_default_actions(self) -> Dict[str, float]:
        """Extract default drone action timings from constants."""
        return DRONE_DEFAULT_ACTION_TIMES.copy()

    def _get_enhanced_action_name_to_time(self) -> Dict[str, float]:
        """Get enhanced action name to time mapping that includes default dog and drone actions."""
        # Start with spreadsheet data and ensure all values are floats
        base_actions = self.spreadsheet_loader.get_action_name_to_time()
        action_name_to_time = {}
        
        # Convert all values to floats
        for name, time_val in base_actions.items():
            try:
                action_name_to_time[name] = float(time_val)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid time value for action '{name}': {time_val}")
                continue
        
        # Add dog default actions
        dog_actions = self._get_dog_default_actions()
        for action, time_val in dog_actions.items():
            if action not in action_name_to_time:
                action_name_to_time[action] = time_val
        
        # Add drone default actions
        drone_actions = self._get_drone_default_actions()
        for action, time_val in drone_actions.items():
            if action not in action_name_to_time:
                action_name_to_time[action] = time_val
        
        self.logger.debug(f"Enhanced action details loaded: {len(action_name_to_time)} actions")
        return action_name_to_time

    def _get_action_time_with_fallback(self, action_name: str, action_name_to_time: Dict[str, Union[str, float]]) -> float:
        """
        Get action time with fallback logic for parameterized drone commands.
        
        Args:
            action_name: The action name to look up
            action_name_to_time: The action mapping dictionary
            
        Returns:
            The action time, or 0 if not found
        """
        action_lower = action_name.lower()
        
        # First try exact match
        if action_name in action_name_to_time:
            value = action_name_to_time[action_name]
            return float(value) if isinstance(value, (str, int, float)) else 0.0
        if action_lower in action_name_to_time:
            value = action_name_to_time[action_lower]
            return float(value) if isinstance(value, (str, int, float)) else 0.0
        
        # For drone actions, try pattern matching
        if action_lower.startswith(("move_", "rotate_", "flip_")):
            # Extract base command (e.g., "move_up_100" -> "move_up")
            parts = action_lower.split('_')
            if len(parts) >= 2:
                base_command = '_'.join(parts[:2])  # e.g., "move_up"
                if base_command in action_name_to_time:
                    return action_name_to_time[base_command]
                    
        # Try more specific drone action patterns
        for pattern, default_time in DRONE_PATTERN_FALLBACK_TIMES.items():
            if action_lower.startswith(pattern):
                return default_time
                
        # Dog action patterns
        for pattern, default_time in DOG_PATTERN_FALLBACK_TIMES.items():
            if action_lower == pattern or action_lower.startswith(pattern):
                return default_time
        
        return 0.0  # Not found

    def compile_actions(self) -> List[Dict[str, Any]]:
        """
        Compile and validate robot actions from spreadsheet data.

        Returns:
            List of dictionaries containing validated robot actions

        Raises:
            ValueError: If actions don't exist or exceed their time allocation
        """
        robot_actions = self.spreadsheet_loader.get_robot_actions()
        action_name_to_time = self._get_enhanced_action_name_to_time()

        for action in robot_actions:
            for key in self._get_robot_keys(action):
                value = action[key]
                # Only render as Jinja2 template if there are template markers and value is not empty
                if value and ("{{" in value or "}}" in value):
                    rtemplate = Environment(loader=BaseLoader).from_string(value)
                    action[key] = rtemplate.render({})

        self.logger.info(f"Compiled {len(robot_actions)} action sequences")
        self.logger.debug(f"Action details loaded: {list(action_name_to_time.keys())}")

        self.check_actions_existence(robot_actions, action_name_to_time, strict_mode=False)
        self.check_actions_time(robot_actions, action_name_to_time)

        return robot_actions

    def check_actions_time(
        self, robot_actions: List[Dict[str, str]], action_name_to_time: Dict[str, Union[str, float]]
    ) -> None:
        """
        Validate that action execution times don't exceed their allocated time slot.

        Args:
            robot_actions: List of robot action sequences
            action_name_to_time: Mapping of action names to execution times

        Raises:
            ValueError: If action times exceed allocated time slot
        """
        for idx, action in enumerate(robot_actions, start=1):
            time_val = action.get("Time")
            for key in self._get_robot_keys(action):
                value = action[key]
                if value:
                    actions = [a.strip() for a in value.splitlines() if a.strip()]
                    total_action_time = 0.0
                    for act in actions:
                        act_time = self._get_action_time_with_fallback(act, action_name_to_time)
                        if act_time > 0:
                            total_action_time += act_time
                    if total_action_time > float(time_val):
                        raise ValueError(
                            f"Row {idx}: Sum of action times {total_action_time}s for '{key}' exceeds overall time {time_val}s"
                        )

    def check_actions_existence(
        self, robot_actions: List[Dict[str, str]], action_name_to_time: Dict[str, Union[str, float]], strict_mode: bool = True
    ) -> None:
        """
        Validate that all specified actions exist in the action details or are known default actions.

        Args:
            robot_actions: List of robot action sequences
            action_name_to_time: Mapping of action names to execution times
            strict_mode: If True, raises ValueError for unknown actions. If False, only logs warnings.

        Raises:
            ValueError: If an action is referenced but not defined in action details or defaults (strict_mode=True)
        """
        for idx, action in enumerate(robot_actions, start=1):
            for key in self._get_robot_keys(action):
                value = action[key]
                if value:
                    actions = [a.strip() for a in value.splitlines() if a.strip()]
                    for act in actions:
                        action_time = self._get_action_time_with_fallback(act, action_name_to_time)
                        if action_time <= 0:
                            error_msg = f"Row {idx}: Action '{act}' for key '{key}' not found in action details or defaults"
                            if strict_mode:
                                raise ValueError(error_msg)
                            else:
                                # Log warning but don't fail - this allows for more flexible action definitions
                                self.logger.warning(f"{error_msg}. This action may use runtime defaults.")
