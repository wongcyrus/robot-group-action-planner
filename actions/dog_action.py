"""
Enhanced Dog Action Implementation with Network Integration

This module provides improved dog action handling with better network communication,
error handling, and status monitoring for Stanford Quadruped Mini Pupper robots.
Uses MovementGroups directly without action mapping.
"""

import threading
import time
from typing import Any, Dict, Optional

import requests

from actions.base_action import BaseAction
from constant import DOG_PATTERN_FALLBACK_TIMES


class DogAction(BaseAction):
    """Enhanced dog action handler with network API integration and MovementGroups support."""

    def __init__(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Optional[Dict[str, int]] = None,
        dog_id: str = "dog_1",
        robot_ip: str = "10.0.0.10",  # Default robot network IP
        robot_port: int = 8830,  # Legacy UDP port - converted to API port
        robot_api_port: Optional[int] = None,  # Direct API port specification
        connection_timeout: float = 5.0,
        action_timeout: float = 30.0,
        **kwargs,  # Accept any additional parameters for backwards compatibility
    ):
        super().__init__(dog_id, action_name_to_time, action_name_to_repeat_time)

        # Ignore any additional kwargs for backwards compatibility
        _ = kwargs

        self.dog_id = dog_id
        self.robot_ip = robot_ip

        # Convert legacy UDP port to API port if not directly specified
        if robot_api_port is not None:
            self.robot_api_port = robot_api_port
        else:
            self.robot_api_port = 8080 if robot_port == 8830 else robot_port + 250

        self.connection_timeout = connection_timeout
        self.action_timeout = action_timeout

        # API endpoints
        self.base_url = f"http://{robot_ip}:{self.robot_api_port}"
        self.status_url = f"{self.base_url}/status"
        self.execute_url = f"{self.base_url}/execute"
        self.stop_url = f"{self.base_url}/stop"
        self.clear_url = f"{self.base_url}/clear"

        self.logger.info(
            f"Enhanced network dog action handler initialized for {self.base_url}"
        )

    def _execute_single_action(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """Execute a single dog action via network API."""

        action_time = self.get_action_time(action_name)
        repeat_count = self.get_repeat_count(action_name)

        # Use default timing if not found in spreadsheet
        if action_time <= 0:
            action_time = self._get_default_action_time(action_name)
            self.logger.info(
                f"Using default timing for dog action '{action_name}': {action_time}s"
            )

        self.logger.info(
            f"Executing dog action '{action_name}' for {action_time}s, {repeat_count} times"
        )

        # Use action name directly (no mapping needed)
        robot_action = action_name.lower()

        for i in range(repeat_count):
            if stop_event and stop_event.is_set():
                return False

            try:
                # Make single API call and sleep for the duration
                success = self._execute_network_command_and_sleep(
                    robot_action, action_time
                )
                if not success:
                    return False

                self.logger.info(
                    f"Completed dog action '{action_name}' iteration {i + 1}/{repeat_count}"
                )

                # Brief pause between repetitions
                if i < repeat_count - 1:
                    time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error executing dog action '{action_name}': {e}")
                return False

        return True

    def _execute_network_command_and_sleep(
        self, action_name: str, duration: float
    ) -> bool:
        """Execute action via network API and sleep for duration."""
        try:
            # Prepare request payload
            payload = {"action": action_name, "duration": duration, "parameters": {}}

            # Add any action-specific parameters from MovementGroups
            parameters = self._get_movement_parameters(action_name, duration)
            if parameters:
                payload["parameters"] = parameters

            self.logger.debug(f"Sending network command: {payload}")

            # Send single request
            response = requests.post(
                self.execute_url, json=payload, timeout=self.connection_timeout
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    self.logger.info(
                        f"Network action '{action_name}' sent successfully, sleeping for {duration}s"
                    )
                    # Sleep for the action duration
                    time.sleep(duration)
                    return True
                else:
                    self.logger.error(
                        f"Network action failed: {result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                self.logger.error(
                    f"Network request failed with status {response.status_code}: {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout executing network action '{action_name}'")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error executing action '{action_name}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error executing action '{action_name}': {e}")
            return False

    def _get_movement_parameters(
        self, action_name: str, duration: float
    ) -> Dict[str, Any]:
        """Get MovementGroups-specific parameters for actions."""
        parameters = {}

        # Use duration for time-based parameters
        time_uni = min(duration, 5.0)  # Cap time_uni to reasonable maximum
        time_acc = min(duration * 0.3, 1.0)  # Acceleration time as fraction of duration

        # Movement actions with velocity parameters
        if action_name.startswith("gait_uni"):
            # Gait with custom velocity
            parameters["v_x"] = 0.15  # Default forward velocity
            parameters["v_y"] = 0.0
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        # Head movement actions
        elif action_name.startswith("head_move"):
            parameters["pitch_deg"] = 0
            parameters["yaw_deg"] = 0
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        elif action_name == "look_up":
            parameters["pitch_deg"] = 20
            parameters["yaw_deg"] = 0
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        elif action_name == "look_down":
            parameters["pitch_deg"] = -20
            parameters["yaw_deg"] = 0
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        elif action_name == "look_left":
            parameters["pitch_deg"] = 0
            parameters["yaw_deg"] = -30
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        elif action_name == "look_right":
            parameters["pitch_deg"] = 0
            parameters["yaw_deg"] = 30
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        # Body movement actions
        elif action_name.startswith("body_row"):
            parameters["row_deg"] = 0
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        elif action_name.startswith("height_move"):
            parameters["ht"] = 0.02  # Default height change
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        # Leg lift actions
        elif action_name.startswith("foreleg_lift") or action_name.startswith(
            "backleg_lift"
        ):
            parameters["leg_index"] = "left"
            parameters["ht"] = 0.01
            parameters["time_uni"] = time_uni
            parameters["time_acc"] = time_acc

        # Rotation actions
        elif action_name.startswith("rotate"):
            parameters["angle"] = 30  # Default rotation angle

        elif action_name.startswith("bowback"):
            parameters["angle"] = 20

        return parameters

    def _get_default_action_time(self, action_name: str) -> float:
        """Get default timing for dog actions using centralized constants."""
        action_name_lower = action_name.lower()

        # Check pattern fallback times
        if action_name_lower in DOG_PATTERN_FALLBACK_TIMES:
            return DOG_PATTERN_FALLBACK_TIMES[action_name_lower]

        # Pattern matching
        for pattern, default_time in DOG_PATTERN_FALLBACK_TIMES.items():
            if action_name_lower == pattern or action_name_lower.startswith(pattern):
                return default_time

        # Default for unknown actions
        return 3.0

    def clear_action_queue(self) -> bool:
        """Clear the robot's action queue."""
        try:
            response = requests.post(self.clear_url, timeout=self.connection_timeout)
            if response.status_code == 200:
                result = response.json()
                self.logger.info(
                    f"Cleared robot action queue: {result.get('message', '')}"
                )
                return result.get("success", False)
            else:
                self.logger.error(
                    f"Clear queue failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            self.logger.error(f"Failed to clear queue: {e}")
            return False

    def execute_action_sync(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """Execute a single action synchronously (for backwards compatibility)."""
        return self._execute_single_action(action_name, stop_event)

    def emergency_stop(self) -> bool:
        """Send emergency stop command to robot."""
        try:
            response = requests.post(self.stop_url, timeout=self.connection_timeout)
            if response.status_code == 200:
                result = response.json()
                self.logger.warning("Emergency stop sent to robot")
                return result.get("success", False)
            else:
                self.logger.error(
                    f"Emergency stop failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            self.logger.error(f"Failed to send emergency stop: {e}")
            return False

    def get_robot_status(self) -> Dict[str, Any]:
        """Get current robot status."""
        try:
            response = requests.get(self.status_url, timeout=self.connection_timeout)
            if response.status_code == 200:
                status = response.json()
                status["connected"] = True
                return status
            else:
                return {
                    "error": f"Status request failed: {response.status_code}",
                    "connected": False,
                }
        except Exception as e:
            return {"error": f"Status request error: {str(e)}", "connected": False}

    def cleanup(self) -> None:
        """Clean up resources and send final stop command."""
        self.logger.info("Cleaning up network dog action handler")

        # Try to send stop command
        try:
            self.emergency_stop()
        except Exception as e:
            self.logger.error(f"Error during cleanup stop command: {e}")

        self.logger.info("Network dog action handler cleanup complete")


# Legacy class alias for backwards compatibility
NetworkDogAction = DogAction
