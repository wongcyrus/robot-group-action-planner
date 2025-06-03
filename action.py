
from typing import Any, Dict, Optional, List
import logging
import requests



class RobotAction:
    """
    A class to handle robot action operations including sending commands 
    and executing predefined actions.
    """
    
    # Dictionary of predefined robot actions
    actions: Dict[str, Dict[str, Any]] = {
        # ...existing code for actions dictionary...
        "back_fast": {"sleep_time": 4.5, "action": ["2", "4"], "name": "back_fast"},
        "bow": {"sleep_time": 4, "action": ["10", "1"], "name": "bow"},
        "chest": {"sleep_time": 9, "action": ["12", "1"], "name": "chest"},
        "dance_eight": {"sleep_time": 85, "action": ["42", "1"], "name": "dance_eight"},
        "dance_five": {"sleep_time": 59, "action": ["39", "1"], "name": "dance_five"},
        "dance_four": {"sleep_time": 59, "action": ["38", "1"], "name": "dance_four"},
        "dance_nine": {"sleep_time": 84, "action": ["43", "1"], "name": "dance_nine"},
        "dance_seven": {"sleep_time": 67, "action": ["41", "1"], "name": "dance_seven"},
        "dance_six": {"sleep_time": 69, "action": ["40", "1"], "name": "dance_six"},
        "dance_ten": {"sleep_time": 85, "action": ["44", "1"], "name": "dance_ten"},
        "dance_three": {"sleep_time": 70, "action": ["37", "1"], "name": "dance_three"},
        "dance_two": {"sleep_time": 52, "action": ["36", "1"], "name": "dance_two"},
        "go_forward": {"sleep_time": 3.5, "action": ["1", "4"], "name": "go_forward"},
        "kung_fu": {"sleep_time": 2, "action": ["46", "2"], "name": "kung_fu"},
        "left_kick": {"sleep_time": 2, "action": ["18", "1"], "name": "left_kick"},
        "left_move_fast": {"sleep_time": 3, "action": ["3", "4"], "name": "left_move_fast"},
        "left_shot_fast": {
            "sleep_time": 4,
            "action": ["13", "1"],
            "name": "left_shot_fast",
        },
        "left_uppercut": {"sleep_time": 2, "action": ["16", "1"], "name": "left_uppercut"},
        "push_ups": {"sleep_time": 9, "action": ["5", "1"], "name": "push_ups"},
        "right_kick": {"sleep_time": 2, "action": ["19", "1"], "name": "right_kick"},
        "right_move_fast": {
            "sleep_time": 3,
            "action": ["4", "4"],
            "name": "right_move_fast",
        },
        "right_shot_fast": {
            "sleep_time": 4,
            "action": ["14", "1"],
            "name": "right_shot_fast",
        },
        "right_uppercut": {
            "sleep_time": 2,
            "action": ["17", "1"],
            "name": "right_uppercut",
        },
        "sit_ups": {"sleep_time": 12, "action": ["6", "1"], "name": "sit_ups"},
        "squat": {"sleep_time": 1, "action": ["11", "1"], "name": "squat"},
        "squat_up": {"sleep_time": 6, "action": ["45", "1"], "name": "squat_up"},
        "stand": {"sleep_time": 1, "action": ["0", "1"], "name": "站立"},
        "stand_up_back": {"sleep_time": 5, "action": ["21", "1"], "name": "stand_up_back"},
        "stand_up_front": {
            "sleep_time": 5,
            "action": ["20", "1"],
            "name": "stand_up_front",
        },
        "stepping": {"sleep_time": 3, "action": ["24", "2"], "name": "stepping"},
        "stop": {"sleep_time": 3, "action": ["24", "2"], "name": "stop"},
        "turn_left": {"sleep_time": 4, "action": ["7", "4"], "name": "turn_left"},
        "turn_right": {"sleep_time": 4, "action": ["8", "4"], "name": "turn_right"},
        "twist": {"sleep_time": 4, "action": ["22", "1"], "name": "twist"},
        "wave": {"sleep_time": 3.5, "action": ["9", "1"], "name": "wave"},
        "weightlifting": {"sleep_time": 9, "action": ["35", "1"], "name": "weightlifting"},
        "wing_chun": {"sleep_time": 2, "action": ["15", "1"], "name": "wing_chun"},
    }
    
    def __init__(self, api_url: str, device_id: str = "1732853986186"):
        """
        Initialize the RobotAction class.
        
        Args:
            api_url: The URL of the robot API
            device_id: The ID of the robot device
        """
        self.api_url = api_url
        self.device_id = device_id
        self.current_action = None
        self.logger = logging.getLogger("RobotAction")
        
        # Configure basic logging if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
    def run_action(self, name:str) -> Optional[Dict[str, Any]]:
        """
        Run a specific robot action with the given parameters.
        
        Args:
            p1: First parameter for the action
            p2: Second parameter for the action
            
        Returns:
            Optional response data from the API call
        """
       
        action =  self.actions[name]
        return self._send_request(
            method="RunAction",
            params=[name, action["sleep_time"]],
            log_success_msg=f"Action run_action({name}, {action["sleep_time"]}) successful.",
            log_error_msg=f"Error running action run_action({name}, {action["sleep_time"]}):",
        )
    
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
    
    def _run_action(self, p1: str, p2: str) -> Optional[Dict[str, Any]]:
        """
        Private method to run an action using the run_action method.
        
        Args:
            p1: First parameter for the action
            p2: Second parameter for the action
            
        Returns:
            Optional response data from the API call
        """
        return self.run_action(p1, p2)
        
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
    
    def execute_action(self, action_item: Dict[str, Any]) -> None:
        """
        Execute a robot action from the predefined actions dictionary.
        
        Args:
            action_item: Dictionary containing the action name to execute
        """
        action_name = action_item["name"]
        action = self.actions[action_name]
        self.current_action = {
            "name": action["name"],
            "sleep_time": action["sleep_time"],
        }
        try:
            self._run_action(action["action"][0], action["action"][1])
        except Exception as e:
            self.logger.error("Error executing action %s: %s", action_name, e)
    
    def get_available_actions(self) -> List[str]:
        """
        Get a list of all available action names.
        
        Returns:
            List of action names
        """
        return list(self.actions.keys())
