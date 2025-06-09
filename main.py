import logging
import os
import threading
import time
from typing import Dict

from action import RobotAction
from action_compiler import ActionCompiler
from song_player import play_song
from spreadsheet_loader import SpreadsheetLoader

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


def initialize_robots(
    action_name_to_time: Dict, action_name_to_repeat_time: Dict
) -> Dict[int, RobotAction]:
    """Initialize all robot connections and return them as a dictionary."""
    robots = {}
    for robot_id, ip_address in ROBOT_IPS.items():
        try:
            robots[robot_id] = RobotAction(
                ip_address, action_name_to_time, action_name_to_repeat_time
            )
            logger.info(f"Robot {robot_id} initialized at {ip_address}")
        except (ConnectionError, OSError, ValueError) as e:
            logger.error(f"Failed to initialize Robot {robot_id}: {e}")
    return robots


def execute_robot_actions(
    robots: Dict[int, RobotAction], row: Dict[str, str], stop_event: threading.Event
) -> None:
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
                t = threading.Thread(target=robot.run_action, args=(action, stop_event))
                threads.append(t)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            while thread.is_alive():
                thread.join(timeout=0.1)
                if stop_event.is_set():
                    logger.info("Stop event set, breaking join loop.")
                    break

        # Wait for the specified time before the next action, but check for stop_event
        logger.info(f"Waiting for {time_value} seconds")
        waited = 0.0
        interval = 0.1
        while waited < float(time_value):
            if stop_event.is_set():
                logger.info("Stop event set during wait, breaking sleep loop.")
                break
            time.sleep(interval)
            waited += interval

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error executing robot actions: {e}")
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user (Ctrl+C)")
        stop_event.set()
        raise


def main() -> None:
    """Main function to load spreadsheet and coordinate robot actions."""

    song_folder = os.path.join(os.path.dirname(__file__), "song")
    stop_event = threading.Event()
    try:
        # Load the spreadsheet data

        song_files = [f for f in os.listdir(song_folder) if f.lower().endswith(".mp4")]
        if not song_files:
            logger.error(f"No .mp4 files found in {song_folder}")
            return

        for song_file in song_files:
            if stop_event.is_set():
                logger.info(
                    "Stop event detected before playing next song. Exiting loop."
                )
                break

            song = os.path.splitext(song_file)[0]
            song_file_path = os.path.join(song_folder, song_file)

            logger.info(
                f"Loading spreadsheet with ID: {ACTION_SEQUENCE_SPREADSHEET_ID} and action details ID: {ACTION_DETAILS_SPREADSHEET_ID}"
            )
            logger.info(f"Current song: {song_file_path}")

            spreadsheet_loader = SpreadsheetLoader(
                ACTION_SEQUENCE_SPREADSHEET_ID, ACTION_DETAILS_SPREADSHEET_ID, song
            )

            action_compiler = ActionCompiler(spreadsheet_loader)
            robot_actions = action_compiler.compile_actions()
            action_name_to_time = spreadsheet_loader.get_action_name_to_time()
            action_name_to_repeat_time = (
                spreadsheet_loader.get_action_name_to_repeat_time()
            )
            robots = initialize_robots(action_name_to_time, action_name_to_repeat_time)

            # Play the song before starting robot actions
            play_song(song_file_path)
            for row in robot_actions:
                logger.info(f"Processing row: {row}")
                try:
                    execute_robot_actions(robots, row, stop_event)
                    if stop_event.is_set():
                        logger.info("Stop event detected in main loop. Exiting...")
                        return
                except KeyboardInterrupt:
                    logger.info("Main loop interrupted by user (Ctrl+C). Exiting...")
                    stop_event.set()
                    return

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"An error occurred in the main program: {e}")
    except KeyboardInterrupt:
        logger.info("Program interrupted by user (Ctrl+C). Exiting...")
        stop_event.set()
        return


if __name__ == "__main__":
    main()
