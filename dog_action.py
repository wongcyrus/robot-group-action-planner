import logging
import threading
import time
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from dog.action_executor import DogActionExecutor


class DogAction:
    """
    Handles dog action operations for robot dogs.
    Provides an interface to execute dog actions like move, stand, hop, etc.
    """

    def __init__(
        self,
        dog_executor: "DogActionExecutor",
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int] = None,
        dog_id: str = "dog_1",
    ):
        """
        Initialize the DogAction class.

        Args:
            dog_executor: The DogActionExecutor instance
            action_name_to_time: Dictionary mapping action names to their execution time
            action_name_to_repeat_time: Dictionary mapping action names to their repeat time
            dog_id: The ID of the dog
        """
        self.dog_executor = dog_executor
        self.dog_id = dog_id
        self.actions = action_name_to_time
        self.repeat_actions = action_name_to_repeat_time or {}
        self.logger = logging.getLogger("DogAction")

        # Validate that the executor is available
        if self.dog_executor is None:
            self.logger.warning("Dog executor is not available - running in test mode")

    def run_action(self, name: str, stop_event: threading.Event = None) -> bool:
        """
        Run one or more dog actions (multi-line supported).

        Args:
            name: Action name(s), possibly multi-line.
            stop_event: Optional threading.Event for interruption.

        Returns:
            True if actions were executed successfully, False otherwise.
        """
        # Handle single or multi-line names: split by newlines if present, else use as single action
        if "\n" in name:
            names = [n.strip() for n in name.splitlines() if n.strip()]
        else:
            names = [name.strip()] if name.strip() else []

        for n in names:
            if stop_event is not None and stop_event.is_set():
                self.logger.info("Dog action interrupted by stop_event.")
                break

            # Get timing information - use default if not found in actions dictionary
            if n in self.actions:
                sleep_time = self.actions[n]
                repeat = self.repeat_actions.get(n, 1)
            else:
                # Use default timing for dog actions not in spreadsheet
                sleep_time = self._get_default_action_time(n)
                repeat = 1
                self.logger.info(
                    f"Using default timing for dog action '{n}': {sleep_time}s"
                )

            # Execute the dog action multiple times if needed
            for _ in range(repeat):
                if stop_event is not None and stop_event.is_set():
                    self.logger.info(
                        "Dog action interrupted by stop_event during repeat."
                    )
                    break

                success = self._execute_dog_command(n)
                if not success:
                    self.logger.error(f"Failed to execute dog action: {n}")

                # Small delay between repeats
                if repeat > 1:
                    time.sleep(0.1)

            # Wait for the specified time
            waited = 0.0
            interval = 0.1
            while waited < float(sleep_time):
                if stop_event is not None and stop_event.is_set():
                    self.logger.info(
                        "Dog action interrupted by stop_event during sleep."
                    )
                    break
                time.sleep(interval)
                waited += interval

        return True

    def _execute_dog_command(self, action_name: str) -> bool:
        """
        Execute a specific dog command based on the action name.

        Args:
            action_name: The name of the action to execute

        Returns:
            True if command was executed successfully, False otherwise.
        """
        if self.dog_executor is None:
            self.logger.warning(
                f"Dog executor not available, simulating action: {action_name}"
            )
            return True

        try:
            # Map action names to dog commands
            action_name_lower = action_name.lower()

            # Extract parameters if present in action name
            parameters = self._extract_parameters(action_name_lower) or {}

            if action_name_lower == "activate":
                self.dog_executor.queue_action("activate", parameters)
                self.logger.info(f"Dog {self.dog_id}: Activate executed")

            elif action_name_lower == "stand_up":
                self.dog_executor.queue_action("stand_up", parameters)
                self.logger.info(f"Dog {self.dog_id}: Stand up executed")

            elif action_name_lower == "lay_down":
                self.dog_executor.queue_action("lay_down", parameters)
                self.logger.info(f"Dog {self.dog_id}: Lay down executed")

            elif action_name_lower.startswith("forward"):
                distance = self._extract_distance(action_name_lower, 50)
                speed = self._extract_speed(action_name_lower, 0.5)
                params = {"distance": distance, "speed": speed}
                self.dog_executor.queue_action("forward", params)
                self.logger.info(
                    f"Dog {self.dog_id}: Move forward {distance} units at speed {speed} executed"
                )

            elif action_name_lower.startswith("back"):
                distance = self._extract_distance(action_name_lower, 50)
                speed = self._extract_speed(action_name_lower, 0.5)
                params = {"distance": distance, "speed": speed}
                self.dog_executor.queue_action("back", params)
                self.logger.info(
                    f"Dog {self.dog_id}: Move back {distance} units at speed {speed} executed"
                )

            elif action_name_lower.startswith("left"):
                distance = self._extract_distance(action_name_lower, 50)
                speed = self._extract_speed(action_name_lower, 0.5)
                params = {"distance": distance, "speed": speed}
                self.dog_executor.queue_action("left", params)
                self.logger.info(
                    f"Dog {self.dog_id}: Move left {distance} units at speed {speed} executed"
                )

            elif action_name_lower.startswith("right"):
                distance = self._extract_distance(action_name_lower, 50)
                speed = self._extract_speed(action_name_lower, 0.5)
                params = {"distance": distance, "speed": speed}
                self.dog_executor.queue_action("right", params)
                self.logger.info(
                    f"Dog {self.dog_id}: Move right {distance} units at speed {speed} executed"
                )

            elif action_name_lower.startswith("cw") or action_name_lower.startswith(
                "rotate_cw"
            ):
                angle = self._extract_angle(action_name_lower, 90)
                speed = self._extract_speed(action_name_lower, 0.5)
                params = {"angle": angle, "speed": speed}
                self.dog_executor.queue_action("cw", params)
                self.logger.info(
                    f"Dog {self.dog_id}: Rotate clockwise {angle}° at speed {speed} executed"
                )

            elif action_name_lower.startswith("ccw") or action_name_lower.startswith(
                "rotate_ccw"
            ):
                angle = self._extract_angle(action_name_lower, 90)
                speed = self._extract_speed(action_name_lower, 0.5)
                params = {"angle": angle, "speed": speed}
                self.dog_executor.queue_action("ccw", params)
                self.logger.info(
                    f"Dog {self.dog_id}: Rotate counter-clockwise {angle}° at speed {speed} executed"
                )

            elif action_name_lower == "hop":
                duration = self._extract_duration(action_name_lower, 1.0)
                params = {"duration": duration}
                self.dog_executor.queue_action("hop", params)
                self.logger.info(f"Dog {self.dog_id}: Hop for {duration}s executed")

            elif action_name_lower == "stop":
                self.dog_executor.queue_action("stop")
                self.logger.info(f"Dog {self.dog_id}: Stop executed")

            elif action_name_lower == "deactivate":
                self.dog_executor.queue_action("deactivate")
                self.logger.info(f"Dog {self.dog_id}: Deactivate executed")

            elif action_name_lower.startswith("dance"):
                duration = self._extract_duration(action_name_lower, 3.0)
                params = {"duration": duration}
                self.dog_executor.queue_action("dance", params)
                self.logger.info(f"Dog {self.dog_id}: Dance for {duration}s executed")

            elif action_name_lower.startswith("custom_movement"):
                # Parse custom movement parameters
                params = self._parse_custom_movement(action_name_lower)
                self.dog_executor.queue_action("custom_movement", params)
                self.logger.info(f"Dog {self.dog_id}: Custom movement executed")

            else:
                self.logger.warning(f"Unknown dog action: {action_name}")
                return False

            return True

        except (ConnectionError, OSError, ValueError) as e:
            self.logger.error(f"Error executing dog command '{action_name}': {e}")
            return False

    def _extract_distance(self, action_name: str, default_distance: int) -> int:
        """Extract distance from action name like 'forward_50' -> 50"""
        parts = action_name.split("_")
        for part in parts[1:]:  # Skip the action name itself
            if part.isdigit():
                return int(part)
        return default_distance

    def _extract_angle(self, action_name: str, default_angle: int) -> int:
        """Extract angle from action name like 'cw_90' -> 90"""
        parts = action_name.split("_")
        for part in parts[1:]:  # Skip the action name itself
            if part.isdigit():
                return int(part)
        return default_angle

    def _extract_speed(self, action_name: str, default_speed: float) -> float:
        """Extract speed from action name like 'forward_50_0.7' -> 0.7"""
        parts = action_name.split("_")
        for part in parts[1:]:  # Skip the action name itself
            try:
                speed = float(part)
                if 0.1 <= speed <= 1.0:  # Valid speed range
                    return speed
            except ValueError:
                continue
        return default_speed

    def _extract_duration(self, action_name: str, default_duration: float) -> float:
        """Extract duration from action name like 'hop_2.5' -> 2.5"""
        parts = action_name.split("_")
        for part in parts[1:]:  # Skip the action name itself
            try:
                duration = float(part)
                if 0.1 <= duration <= 10.0:  # Valid duration range
                    return duration
            except ValueError:
                continue
        return default_duration

    def _extract_parameters(self, action_name: str) -> Optional[Dict[str, float]]:
        """Extract parameters from action name"""
        # This is a placeholder for more complex parameter extraction
        # Can be extended based on specific needs
        _ = action_name  # Silence unused parameter warning
        return None

    def _parse_custom_movement(self, action_name: str) -> Dict[str, float]:
        """
        Parse custom movement parameters from action name.

        Example: custom_movement_x_0.5_y_0.3_duration_2.0

        Args:
            action_name: The action name to parse

        Returns:
            Dictionary of movement parameters
        """
        params = {}
        parts = action_name.split("_")

        try:
            i = 1  # Skip 'custom' and 'movement'
            while i < len(parts) - 1:
                if parts[i] in ["x", "y", "duration", "speed"]:
                    key = parts[i]
                    value = float(parts[i + 1])
                    params[key] = value
                    i += 2
                else:
                    i += 1
        except (ValueError, IndexError):
            self.logger.warning(
                f"Could not parse custom movement parameters from: {action_name}"
            )

        return params

    def _get_default_action_time(self, action_name: str) -> float:
        """
        Get default timing for dog actions that aren't in the actions dictionary.

        Args:
            action_name: The name of the dog action

        Returns:
            Default time in seconds for the action
        """
        action_name_lower = action_name.lower()

        # Define default timings for different types of dog actions
        if action_name_lower in ["activate", "deactivate"]:
            return 1.0  # Status changes are quick
        elif action_name_lower in ["stand_up", "lay_down"]:
            return 2.0  # Posture changes take a bit longer
        elif action_name_lower.startswith(("forward", "back", "left", "right")):
            return 2.0  # Movement actions
        elif action_name_lower.startswith(("cw", "ccw", "rotate")):
            return 2.0  # Rotation actions
        elif action_name_lower == "hop":
            return 1.5  # Hop action
        elif action_name_lower == "stop":
            return 0.5  # Stop is immediate
        elif action_name_lower.startswith("dance"):
            return 3.0  # Dance actions take longer
        elif action_name_lower.startswith("custom_movement"):
            return 2.0  # Custom movements
        else:
            return 2.0  # Default for unknown actions

    def emergency_stop(self):
        """Emergency stop the dog."""
        try:
            if self.dog_executor is None:
                self.logger.warning(
                    "Dog executor not available, simulating emergency stop"
                )
                return
            self.dog_executor.stop_immediate()
            self.logger.info(f"Dog {self.dog_id}: Emergency stop executed")
        except (AttributeError, ValueError) as e:
            self.logger.error(f"Error executing emergency stop: {e}")

    def get_status(self) -> Dict[str, any]:
        """
        Get the current status of the dog.

        Returns:
            Dictionary containing dog status information
        """
        try:
            if self.dog_executor is None:
                return {
                    "dog_id": self.dog_id,
                    "status": "test_mode",
                    "message": "Dog executor not available",
                }
            return {
                "dog_id": self.dog_id,
                "is_running": self.dog_executor.is_running,
                "current_action": self.dog_executor.current_action,
                "queue_size": self.dog_executor.action_queue.qsize(),
                "execution_stats": self.dog_executor.execution_stats,
            }
        except (AttributeError, ValueError) as e:
            self.logger.error(f"Error getting status: {e}")
            return {"error": str(e)}
