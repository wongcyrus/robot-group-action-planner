import logging
import os
import threading
import time
from typing import Dict

from action import RobotAction
from action_compiler import ActionCompiler
from constant import ROBOT_IPS
from song_player import play_song, stop_song
from spreadsheet_loader import SpreadsheetLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_robots(
    action_name_to_time: Dict, action_name_to_repeat_time: Dict
) -> Dict[int, RobotAction]:
    """Initialize all robot connections and return them as a dictionary."""
    robots = {}
    for idx, ip_address in enumerate(ROBOT_IPS):
        robot_id = idx + 1
        try:
            robots[robot_id] = RobotAction(
                ip_address, action_name_to_time, action_name_to_repeat_time, "robot_"+ str(robot_id)
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

        logger.info(f"Waiting for {time_value} seconds")
        # Wait for all threads to complete
        for thread in threads:
            while thread.is_alive():
                thread.join(timeout=0.1)
                if stop_event.is_set():
                    logger.info("Stop event set, breaking join loop.")
                    break
        logger.info("All robot actions completed successfully.")                    

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error executing robot actions: {e}")
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user (Ctrl+C)")
        stop_event.set()
        raise


def get_song_files(song_folder: str):
    """Return a list of .mp4 song files in the given folder."""
    return [f for f in os.listdir(song_folder) if f.lower().endswith(".mp4")]


def process_song(song_file_path: str, song: str, stop_event: threading.Event):
    """Process a single song: load spreadsheet, compile actions, and coordinate robots."""
    spreadsheet_loader = SpreadsheetLoader(song)
    action_compiler = ActionCompiler(spreadsheet_loader)
    robot_actions = action_compiler.compile_actions()
    action_name_to_time = spreadsheet_loader.get_action_name_to_time()
    action_name_to_repeat_time = spreadsheet_loader.get_action_name_to_repeat_time()
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
    stop_song()


def main() -> None:
    """Main function to load spreadsheet and coordinate robot actions."""
    song_folder = os.path.join(os.path.dirname(__file__), "song")
    stop_event = threading.Event()
    try:
        # Load the spreadsheet data
        song_files = get_song_files(song_folder)
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

            logger.info(f"Current song: {song_file_path}")
            process_song(song_file_path, song, stop_event)
            time.sleep(3)

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"An error occurred in the main program: {e}")
    except KeyboardInterrupt:
        logger.info("Program interrupted by user (Ctrl+C). Exiting...")
        stop_event.set()
        return


if __name__ == "__main__":
    main()
