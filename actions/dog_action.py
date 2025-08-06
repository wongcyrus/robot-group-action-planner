"""
Updated dog_action.py implementing BaseAction.
"""

import threading
from typing import Dict, Optional

from actions.base_action import BaseAction
from constant import DOG_PATTERN_FALLBACK_TIMES


class DogAction(BaseAction):
    """Updated dog action handler implementing BaseAction interface."""

    def __init__(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Optional[Dict[str, int]] = None,
        dog_executor=None,
        dog_id: str = "dog_1",
        robot_ip: str = "127.0.0.1",
        robot_port: int = 8830,
    ):
        super().__init__(dog_id, action_name_to_time, action_name_to_repeat_time)
        self.dog_executor = dog_executor
        self.dog_id = dog_id
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        if not self.dog_executor:
            self._initialize_dog_executor()

    def _initialize_dog_executor(self):
        """Initialize dog executor."""
        try:
            from driver.dog.action_executor import DogActionExecutor

            self.dog_executor = DogActionExecutor(
                robot_name=self.dog_id,
                robot_ip=self.robot_ip,
                robot_port=self.robot_port,
            )
            self.logger.info("Dog executor initialized successfully")
        except ImportError:
            self.logger.warning("Dog module not available, using simulation mode")
        except Exception as e:
            self.logger.error(f"Failed to initialize dog executor: {e}")

    def _execute_single_action(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """Execute a single dog action."""
        action_time = self.get_action_time(action_name)
        repeat_count = self.get_repeat_count(action_name)

        # If action not found in spreadsheet, use default timing like original version
        if action_time <= 0:
            action_time = self._get_default_action_time(action_name)
            self.logger.info(
                f"Using default timing for dog action '{action_name}': {action_time}s"
            )

        self.logger.info(
            f"Executing dog action '{action_name}' for {action_time}s, {repeat_count} times"
        )

        for i in range(repeat_count):
            if stop_event and stop_event.is_set():
                return False

            try:
                success = self._execute_dog_command(action_name, action_time)
                if not success:
                    return False

                self.logger.info(
                    f"Completed dog action '{action_name}' iteration {i + 1}/{repeat_count}"
                )

            except Exception as e:
                self.logger.error(f"Error executing dog action '{action_name}': {e}")
                return False

        return True

    def _get_default_action_time(self, action_name: str) -> float:
        """
        Get default timing for dog actions that aren't in the actions dictionary.
        Uses centralized constants from constant.py.
        """
        action_name_lower = action_name.lower()

        # Check if action exists in our pattern fallback times
        if action_name_lower in DOG_PATTERN_FALLBACK_TIMES:
            return DOG_PATTERN_FALLBACK_TIMES[action_name_lower]

        # Fallback logic for actions that match patterns
        for pattern, default_time in DOG_PATTERN_FALLBACK_TIMES.items():
            if action_name_lower == pattern or action_name_lower.startswith(pattern):
                return default_time

        # Default for completely unknown actions
        return 3.0

    def _execute_dog_command(self, action_name: str, duration: float) -> bool:
        """Execute specific dog command with no retries."""
        if not self.dog_executor:
            # Simulation mode - timing controlled by execution engine
            self.logger.info(f"Simulating dog action: {action_name}")
            return True

        try:
            # Execute action via dog executor - single attempt only
            # Note: dog_executor already handles timing/duration internally
            success = self.dog_executor.execute_action(action_name, duration)
            if success:
                self.logger.info(f"Dog action '{action_name}' executed successfully")
            else:
                self.logger.error(f"Dog action '{action_name}' failed (no retries)")
            return success

        except Exception as e:
            self.logger.error(f"Failed to execute dog command '{action_name}' (no retries): {e}")
            return False

    def cleanup(self) -> None:
        """Clean up dog resources."""
        if self.dog_executor:
            try:
                self.dog_executor.cleanup()
                self.logger.info("Dog executor cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error during dog cleanup: {e}")
        self.logger.info("Cleaning up dog action handler")
