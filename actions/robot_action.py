"""
Updated action.py implementing BaseAction.
"""

import threading
import time
from typing import Dict, Optional

import requests

from actions.base_action import BaseAction


class RobotAction(BaseAction):
    """Updated robot action handler implementing BaseAction interface."""

    def __init__(
        self,
        api_url: str,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Optional[Dict[str, int]] = None,
        robot_id: str = "robot_1",
    ):
        super().__init__(robot_id, action_name_to_time, action_name_to_repeat_time)
        self.api_url = api_url.rstrip("/")
        self.base_url = f"{self.api_url}/robot"

    def _execute_single_action(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """Execute a single robot action via HTTP API."""
        action_time = self.get_action_time(action_name)
        repeat_count = self.get_repeat_count(action_name)

        if action_time <= 0:
            self.logger.warning(f"Action '{action_name}' not found or has invalid time")
            return False

        self.logger.info(
            f"Executing robot action '{action_name}' for {action_time}s, {repeat_count} times"
        )

        for i in range(repeat_count):
            if stop_event and stop_event.is_set():
                return False

            try:
                # Send action command to robot
                response = requests.post(
                    f"{self.base_url}/action",
                    json={"action": action_name, "duration": action_time},
                    timeout=30,
                )

                if response.status_code == 200:
                    self.logger.info(f"Robot action '{action_name}' sent successfully")
                    time.sleep(action_time)  # Wait for action completion
                    self.logger.info(
                        f"Completed robot action '{action_name}' iteration {i + 1}/{repeat_count}"
                    )
                else:
                    self.logger.error(
                        f"Failed to send robot action '{action_name}': {response.status_code}"
                    )
                    return False

            except requests.RequestException as e:
                self.logger.error(
                    f"Network error sending robot action '{action_name}': {e}"
                )
                return False

        return True

    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info(f"Cleaning up robot action handler for {self.robot_id}")


# Backward compatibility alias
Action = RobotAction
