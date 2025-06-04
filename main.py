from action_compiler import ActionCompiler
from spreadsheet_loader import SpreadsheetLoader
from action import RobotAction
import time
import threading
import logging
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
# ACTION_SEQUENCE_SPREADSHEET_ID = "1JmjO4Yidu2pLtJxEuu4mYPX14AYmEj0przne75JBg6Y"
ACTION_SEQUENCE_SPREADSHEET_ID = "17DqsmqCkoggsNeH2iFZmZ696U30Nz7OmWw8KzJj1B6k"

ACTION_DETAILS_SPREADSHEET_ID = "1Bsgc60s3m_-dxhneTedxFlCCYxEp-9Ippu3Yr8dekxo"

ROBOT_IPS = {
    1: "http://192.168.137.7:9030",
    2: "http://192.168.137.2:9030",
    3: "http://192.168.137.3:9030",
    4: "http://192.168.137.4:9030",
    5: "http://192.168.137.5:9030",
    6: "http://192.168.137.6:9030",
}


def initialize_robots(action_name_to_time: Dict, action_name_to_repeat_time: Dict) -> Dict[int, RobotAction]:
    """Initialize all robot connections and return them as a dictionary."""
    robots = {}
    for robot_id, ip_address in ROBOT_IPS.items():
        try:
            robots[robot_id] = RobotAction(ip_address, action_name_to_time, action_name_to_repeat_time)
            logger.info(f"Robot {robot_id} initialized at {ip_address}")
        except Exception as e:
            logger.error(f"Failed to initialize Robot {robot_id}: {e}")
    return robots


def execute_robot_actions(robots: Dict[int, RobotAction], row: Dict[str, str]) -> None:
    """Execute robot actions from a row of spreadsheet data."""
    try:
        time_value = row["Time"]
        logger.info(f"Executing actions with time value: {time_value}")

        # Create threads for all robots with actions
        threads = []
        for robot_id, robot in robots.items():
            action_key = f"Robot_{robot_id}"
            action = row.get(action_key)

            if action:
                logger.info(f"Robot {robot_id} will perform: {action}")
                threads.append(
                    threading.Thread(target=robot.run_action, args=(action,))
                )

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Wait for the specified time before the next action
        logger.info(f"Waiting for {time_value} seconds")
        time.sleep(float(time_value))

    except Exception as e:
        logger.error(f"Error executing robot actions: {e}")


def main() -> None:
    """Main function to load spreadsheet and coordinate robot actions."""
    try:
        # Load the spreadsheet data
        logger.info(
            f"Loading spreadsheet with ID: {ACTION_SEQUENCE_SPREADSHEET_ID} and action details ID: {ACTION_DETAILS_SPREADSHEET_ID}"
        )
        spreadsheet_loader = SpreadsheetLoader(
            ACTION_SEQUENCE_SPREADSHEET_ID, ACTION_DETAILS_SPREADSHEET_ID
        )

        action_compiler = ActionCompiler(spreadsheet_loader)
        robot_actions = action_compiler.compile_actions()
        action_name_to_time = spreadsheet_loader.get_action_name_to_time()
        action_name_to_repeat_time = spreadsheet_loader.get_action_name_to_repeat_time()
        robots = initialize_robots(action_name_to_time, action_name_to_repeat_time)

        for row in robot_actions:
            logger.info(f"Processing row: {row}")
            execute_robot_actions(robots, row)

        logger.info("All robot actions completed successfully")

    except Exception as e:
        logger.error(f"An error occurred in the main program: {e}")


if __name__ == "__main__":
    main()
