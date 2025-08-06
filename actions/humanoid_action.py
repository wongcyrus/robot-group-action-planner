"""
Updated humanoid_action.py implementing BaseAction.
"""

import threading
import time
from typing import Any, Dict, Optional

import requests

from actions.base_action import BaseAction
from constant import SESSION_KEY, SIMULATOR_BASE_URL


class HumanoidAction(BaseAction):
    """Updated humanoid action handler implementing BaseAction interface."""

    def __init__(
        self,
        api_url: str,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Optional[Dict[str, int]] = None,
        robot_id: str = "humanoid_1",
    ):
        super().__init__(robot_id, action_name_to_time, action_name_to_repeat_time)
        self.api_url = api_url

    def _execute_single_action(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """Execute a single humanoid action using the same format as original RobotAction."""
        action_time = self.get_action_time(action_name)
        repeat_count = self.get_repeat_count(action_name)

        if action_time <= 0:
            self.logger.warning(f"Action '{action_name}' not found or has invalid time")
            return False

        self.logger.info(
            f"Executing humanoid action '{action_name}' for {action_time}s, {repeat_count} times"
        )

        # Send local request (JSON-RPC format like original)
        result = self._send_local_request(
            method="RunAction",
            params=[action_name, repeat_count],
            log_success_msg=f"Action run_action({action_name}, {repeat_count}) successful.",
            log_error_msg=f"Error running action run_action({action_name}, {repeat_count}):",
        )
        
        if result is None:
            return False

        # Send to simulator (same format as original)
        simulator_result = self._send_to_simulator(
            action_name=action_name,
            robot_id=self.robot_id,
            log_success_msg=f"Simulator action {action_name} for robot {self.robot_id} successful.",
            log_error_msg=f"Error sending action {action_name} to simulator for robot {self.robot_id}:",
        )

        # Wait for action completion (same timing logic as original)
        waited = 0.0
        interval = 0.1
        while waited < float(action_time):
            if stop_event and stop_event.is_set():
                self.logger.info("Action interrupted by stop_event during sleep.")
                return False
            time.sleep(interval)
            waited += interval

        return True

    def _send_local_request(
        self,
        method: str,
        params: Optional[list],
        log_success_msg: str,
        log_error_msg: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an API request to the robot using JSON-RPC format (same as original).

        Args:
            method: The API method to call
            params: List of parameters for the API call
            log_success_msg: Message to log on successful API call
            log_error_msg: Message to log on failed API call

        Returns:
            Optional response data from the API call
        """
        headers = {"deviceid": "12345"}
        data = {
            "id": "12345",
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:
            data["params"] = params
        try:
            response = requests.post(
                self.api_url, headers=headers, json=data, timeout=0.5
            )
            response.raise_for_status()
            resp_json = response.json()
            self.logger.info(
                "%s - %s Response: %s", self.robot_id, log_success_msg, resp_json
            )
            return resp_json
        except requests.exceptions.RequestException as e:
            self.logger.error("%s %s", log_error_msg, e)
            return None

    def _send_to_simulator(
        self,
        action_name: str,
        robot_id: str,
        log_success_msg: str = None,
        log_error_msg: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an action command to the robot simulator (same format as original).

        Args:
            action_name: The name of the action to execute
            robot_id: The ID of the robot to control
            log_success_msg: Message to log on successful API call
            log_error_msg: Message to log on failed API call

        Returns:
            Optional response data from the simulator API call
        """
        if SIMULATOR_BASE_URL is None:
            self.logger.error("Simulator base URL is not set.")
            return None

        if log_success_msg is None:
            log_success_msg = (
                f"Simulator action {action_name} for robot {robot_id} successful."
            )
        if log_error_msg is None:
            log_error_msg = (
                f"Error sending action {action_name} to simulator for robot {robot_id}:"
            )

        # Construct the URL in the format (same as original):
        if robot_id.startswith("humanoid_"):
            robot_id = robot_id.replace("humanoid_", "robot_")
        url = f"{SIMULATOR_BASE_URL}/run_action/{robot_id}?session_key={SESSION_KEY}"

        # Prepare the payload in the expected format: {"action": "bow"}
        payload = {"action": action_name}

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=5.0,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            resp_json = response.json()
            self.logger.info(
                "%s - %s Response: %s", self.robot_id, log_success_msg, resp_json
            )
            return resp_json
        except requests.exceptions.RequestException as e:
            self.logger.error("%s %s", log_error_msg, e)
            return None

    def run_stop_action(self) -> Optional[Dict[str, Any]]:
        """Stop any currently running robot action (same as original)."""
        return self._send_local_request(
            method="StopBusServo",
            params=["stopAction"],
            log_success_msg="Action run_stop_action() successful.",
            log_error_msg="Error running action run_stop_action():",
        )

    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info(f"Cleaning up humanoid action handler for {self.robot_id}")


# Backward compatibility alias
Action = HumanoidAction
