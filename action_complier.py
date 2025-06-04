from spreadsheet_loader import SpreadsheetLoader


class ActionCompiler:

    def __init__(self, spreadsheet_loader: SpreadsheetLoader):
        self.spreadsheet_loader = spreadsheet_loader

    def compile_actions(self):
   
        robot_actions = self.spreadsheet_loader.get_robot_actions()
        # print(self.spreadsheet_loader.get_action_details())
        action_name_to_time = self.spreadsheet_loader.get_action_name_to_time()
        
        print("Action details loaded:", action_name_to_time)

        self.check_actions_existence(robot_actions, action_name_to_time)
        self.check_actions_time(robot_actions, action_name_to_time)
    

        return robot_actions

    def check_actions_time(self, robot_actions, action_name_to_time):
        for idx, action in enumerate(robot_actions, start=1):
            print(f"Processing action: {action}")
            time = action.get("Time")
            action_keys = [key for key in action if key.startswith("Robot")]
            action_times = [action_name_to_time.get(action[key], "") for key in action_keys if action[key] != ""]
            if any(action_time != "" and float(action_time) > float(time) for action_time in action_times):
                raise ValueError(
                    f"Row {idx}: Action time(s) {action_times} must be less than or equal to overall time {time}s"
                )

    def check_actions_existence(self, robot_actions, action_name_to_time):
        for idx, action in enumerate(robot_actions, start=1):
            for key in action:
                if key.startswith("Robot"):
                    if action[key] != "" and action[key] not in action_name_to_time:
                        raise ValueError(
                            f"Row {idx}: Action '{action[key]}' for key '{key}' not found in action_name_to_time"
                        )