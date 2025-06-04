from typing import Any, Dict, Optional
import logging
import requests
import time


class RobotAction:
    """
    A class to handle robot action operations including sending commands
    and executing predefined actions.

    This class provides an interface to communicate with robot APIs and
    execute actions defined in the action details spreadsheet.
    """

    def __init__(
        self,
        api_url: str,
        action_name_to_time: Dict[str, str],
        device_id: str = "1732853986186",
    ):
        """
        Initialize the RobotAction class.

        Args:
            api_url: The URL of the robot API
            action_name_to_time: Dictionary mapping action names to their execution time
            device_id: The ID of the robot device
        """
        self.api_url = api_url
        self.device_id = device_id
        self.actions = action_name_to_time
        self.logger = logging.getLogger("RobotAction")

    def run_action(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Run a specific robot action or sequence of actions.

        This method supports multi-line action names, where each line represents
        a separate action to be executed in sequence.

        Args:
            name: The name of the action(s) to run, can be multi-line

        Returns:
            Optional response data from the last API call
        """
        # Handle multi-line names: split by newlines, strip whitespace, and filter out empty names
        names = [n.strip() for n in name.splitlines() if n.strip()]
        results = []

        for n in names:
            self.logger.info(f"Running action: {n}")
            if n not in self.actions:
                self.logger.error(f"Action '{n}' not found in actions dictionary.")
                continue

            sleep_time = self.actions[n]
            result = self._send_request(
                method="RunAction",
                params=[n, sleep_time],
                log_success_msg=f"Action run_action({n}, {sleep_time}) successful.",
                log_error_msg=f"Error running action run_action({n}, {sleep_time}):",
            )
            results.append(result)

            # If executing multiple actions, wait for the specified time between them
            if len(names) > 1:
                time.sleep(float(sleep_time))

        return results[-1] if results else None

    def run_stop_action(self) -> Optional[Dict[str, Any]]:
        """
        Stop any currently running robot action.

        Returns:
            Optional response data from the API call
        """
        return self._send_request(
            method="StopBusServo",
            params=["stopAction"],
            log_success_msg="Action run_stop_action() successful.",
            log_error_msg="Error running action run_stop_action():",
        )

    def _run_action(self, p1: str) -> Optional[Dict[str, Any]]:
        """
        Private method to run an action using the run_action method.

        Args:
            p1: First parameter for the action
            p2: Second parameter for the action

        Returns:
            Optional response data from the API call
        """
        return self.run_action(p1)

    def _send_request(
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
        headers = {"deviceid": self.device_id}
        data = {
            "id": self.device_id,
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
            self.logger.info("%s Response: %s", log_success_msg, response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error("%s %s", log_error_msg, e)
            return None
