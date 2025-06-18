import logging
import time
from typing import Any, Dict, Optional

import requests

from constant import SESSION_KEY, SIMULATOR_BASE_URL


class RobotAction:
    """
    Handles robot action operations including sending commands and executing predefined actions.
    Provides an interface to communicate with robot APIs and execute actions defined in the action details spreadsheet.
    """

    def __init__(
        self,
        api_url: str,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int] = None,
        robot_id: str = "1732853986186",
    ):
        """
        Initialize the RobotAction class.

        Args:
            api_url: The URL of the robot API
            action_name_to_time: Dictionary mapping action names to their execution time
            action_name_to_repeat_time: Dictionary mapping action names to their repeat time
            device_id: The ID of the robot device
        """
        self.api_url = api_url
        self.robot_id = robot_id
        self.actions = action_name_to_time
        self.repeat_actions = action_name_to_repeat_time or {}
        self.logger = logging.getLogger("RobotAction")

    def run_action(self, name: str, stop_event=None) -> Optional[Dict[str, Any]]:
        """
        Run one or more robot actions (multi-line supported).

        Args:
            name: Action name(s), possibly multi-line.
            stop_event: Optional threading.Event for interruption.

        Returns:
            Optional response data from the last API call.
        """
        # Handle single or multi-line names: split by newlines if present, else use as single action
        if "\n" in name:
            names = [n.strip() for n in name.splitlines() if n.strip()]
        else:
            names = [name.strip()] if name.strip() else []
        results = []

        for n in names:
            if stop_event is not None and stop_event.is_set():
                self.logger.info("Action interrupted by stop_event.")
                break
            # self.logger.info(f"Running action: {n}")
            if n not in self.actions:
                self.logger.error(f"Action '{n}' not found in actions dictionary.")
                continue

            sleep_time = self.actions[n]
            repeat = self.repeat_actions.get(n, 1)
            result = self._send_local_request(
                method="RunAction",
                params=[n, repeat],
                log_success_msg=f"Action run_action({n}, {repeat}) successful.",
                log_error_msg=f"Error running action run_action({n}, {repeat}):",
            )
            results.append(result)
            result = self._send_to_simulator(
                action_name=n,
                robot_id=self.robot_id,
                log_success_msg=f"Simulator action {n} for robot {self.robot_id} successful.",
                log_error_msg=f"Error sending action {n} to simulator for robot {self.robot_id}:",
            )
            results.append(result)

            waited = 0.0
            interval = 0.1
            while waited < float(sleep_time):
                if stop_event is not None and stop_event.is_set():
                    self.logger.info("Action interrupted by stop_event during sleep.")
                    break
                time.sleep(interval)
                waited += interval

        return results[-1] if results else None

    def run_stop_action(self) -> Optional[Dict[str, Any]]:
        """Stop any currently running robot action."""
        return self._send_local_request(
            method="StopBusServo",
            params=["stopAction"],
            log_success_msg="Action run_stop_action() successful.",
            log_error_msg="Error running action run_stop_action():",
        )

    def _send_local_request(
        self,
        method: str,
        params: Optional[list],
        log_success_msg: str,
        log_error_msg: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an API request to the robot.

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
        Send an action command to the robot simulator.

        Args:
            action_name: The name of the action to execute
            robot_id: The ID of the robot to control
            session_key: The session key for authentication
            simulator_base_url: The base URL of the simulator (default: http://localhost:5000)
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

        # Construct the URL in the format:
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
