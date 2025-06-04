from typing import Dict, List, Any
from spreadsheet_loader import SpreadsheetLoader
import logging
from jinja2 import Environment, BaseLoader


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
        """Helper to get all robot keys in an action row."""
        return [key for key in action if key.startswith("Robot")]

    def compile_actions(self) -> List[Dict[str, Any]]:
        """
        Compile and validate robot actions from spreadsheet data.

        Returns:
            List of dictionaries containing validated robot actions

        Raises:
            ValueError: If actions don't exist or exceed their time allocation
        """
        robot_actions = self.spreadsheet_loader.get_robot_actions()
        action_name_to_time = self.spreadsheet_loader.get_action_name_to_time()

        for action in robot_actions:
            for key in self._get_robot_keys(action):
                value = action[key]
                # Only render as Jinja2 template if there are template markers and value is not empty
                if value and ("{{" in value or "}}" in value):
                    rtemplate = Environment(loader=BaseLoader).from_string(value)
                    action[key] = rtemplate.render({})

        self.logger.info(f"Compiled {len(robot_actions)} action sequences")
        self.logger.debug(f"Action details loaded: {list(action_name_to_time.keys())}")

        self.check_actions_existence(robot_actions, action_name_to_time)
        self.check_actions_time(robot_actions, action_name_to_time)

        return robot_actions

    def check_actions_time(
        self, robot_actions: List[Dict[str, str]], action_name_to_time: Dict[str, str]
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
                        act_time = action_name_to_time.get(act, "")
                        if act_time == "":
                            continue  # Existence is checked elsewhere
                        total_action_time += float(act_time)
                    if total_action_time > float(time_val):
                        raise ValueError(
                            f"Row {idx}: Sum of action times {total_action_time}s for '{key}' exceeds overall time {time_val}s"
                        )

    def check_actions_existence(
        self, robot_actions: List[Dict[str, str]], action_name_to_time: Dict[str, str]
    ) -> None:
        """
        Validate that all specified actions exist in the action details.

        Args:
            robot_actions: List of robot action sequences
            action_name_to_time: Mapping of action names to execution times

        Raises:
            ValueError: If an action is referenced but not defined in action details
        """
        for idx, action in enumerate(robot_actions, start=1):
            for key in self._get_robot_keys(action):
                value = action[key]
                if value:
                    actions = [a.strip() for a in value.splitlines() if a.strip()]
                    for act in actions:
                        if act not in action_name_to_time:
                            raise ValueError(
                                f"Row {idx}: Action '{act}' for key '{key}' not found in action_name_to_time"
                            )
