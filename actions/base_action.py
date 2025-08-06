"""
Base action interface for all robot types.
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseAction(ABC):
    """
    Abstract base class for all robot actions.
    Provides common functionality for action execution.
    """

    def __init__(
        self,
        robot_id: str,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize the base action handler.

        Args:
            robot_id: Unique identifier for the robot
            action_name_to_time: Mapping of action names to execution times
            action_name_to_repeat_time: Mapping of action names to repeat counts
        """
        self.robot_id = robot_id
        self.actions = action_name_to_time
        self.repeat_actions = action_name_to_repeat_time or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{robot_id}")

    def run_action(
        self, name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """
        Run one or more actions (multi-line supported).

        Args:
            name: Action name(s), possibly multi-line
            stop_event: Optional event for stopping execution

        Returns:
            True if all actions executed successfully, False otherwise
        """
        if not name or not name.strip():
            self.logger.warning("Empty action name provided")
            return False

        # Handle multi-line actions
        action_names = self._parse_action_names(name)

        try:
            for action_name in action_names:
                if stop_event and stop_event.is_set():
                    self.logger.info("Stop event detected, aborting action execution")
                    return False

                success = self._execute_single_action(action_name, stop_event)
                if not success:
                    self.logger.error(f"Failed to execute action: {action_name}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error executing actions: {e}")
            return False

    def _parse_action_names(self, name: str) -> List[str]:
        """Parse action names from potentially multi-line string."""
        if "\n" in name:
            return [n.strip() for n in name.splitlines() if n.strip()]
        return [name.strip()]

    @abstractmethod
    def _execute_single_action(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """
        Execute a single action on the specific robot type.

        Args:
            action_name: Name of the action to execute
            stop_event: Optional event for stopping execution

        Returns:
            True if action executed successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement _execute_single_action")

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources when done with the robot."""
        raise NotImplementedError("Subclasses must implement cleanup")

    def get_action_time(self, action_name: str) -> float:
        """Get the execution time for an action."""
        return self.actions.get(action_name, 0.0)

    def get_repeat_count(self, action_name: str) -> int:
        """Get the repeat count for an action."""
        return self.repeat_actions.get(action_name, 1)
