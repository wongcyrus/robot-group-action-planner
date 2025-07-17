import logging
import os
import threading
import time
from typing import Dict

import requests

from action import RobotAction
from action_compiler import ActionCompiler
from constant import ROBOT_IPS, SESSION_KEY, SIMULATOR_BASE_URL, SONG_BUCKET
from djitellopy import Tello
from drone_action import DroneAction
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
                ip_address,
                action_name_to_time,
                action_name_to_repeat_time,
                "robot_" + str(robot_id),
            )
            logger.info(f"Robot {robot_id} initialized at {ip_address}")
        except (ConnectionError, OSError, ValueError) as e:
            logger.error(f"Failed to initialize Robot {robot_id}: {e}")
    return robots


SIMULATOR = True


def initialize_drones(
    action_name_to_time: Dict, action_name_to_repeat_time: Dict
) -> Dict[int, DroneAction]:
    """Initialize all drones and return them as a dictionary."""

    if SIMULATOR:
        simulator_ip = "192.168.25.128"
        drone1 = Tello(host=simulator_ip, control_udp=8889, state_udp=8890)
        drone2 = Tello(host=simulator_ip, control_udp=8890, state_udp=8891)
    else:
        drone_hosts = ["192.168.137.21", "192.168.137.22"]
        # Real drone
        drone1 = Tello(host=drone_hosts[0])
        drone2 = Tello(host=drone_hosts[1])
    drones = [drone1, drone2]

    drone1.connect()
    drone2.connect()

    # Create DroneAction instances
    drone_action1 = DroneAction(
        drone1,
        action_name_to_time,
        action_name_to_repeat_time,
        "drone_1",
    )
    drone_action2 = DroneAction(
        drone2,
        action_name_to_time,
        action_name_to_repeat_time,
        "drone_2",
    )

    drones = {1: drone_action1, 2: drone_action2}
    return drones


def execute_robot_actions(
    robots: Dict[int, RobotAction],
    drones: Dict[int, DroneAction],
    row: Dict[str, str],
    stop_event: threading.Event,
) -> None:
    """Execute robot and drone actions from a row of spreadsheet data."""
    try:
        time_value = row["Time"]
        logger.info(f"Executing actions with time value: {time_value}")

        # Create threads for all robots with actions
        threads = []

        # Process robot actions
        for robot_id, robot in robots.items():
            action_key = f"Robot_{robot_id}"
            action = row.get(action_key)

            if action:
                logger.info(f"Robot {robot_id} will perform: {action}")
                t = threading.Thread(target=robot.run_action, args=(action, stop_event))
                threads.append(t)

        # Process drone actions
        for drone_id, drone in drones.items():
            action_key = f"Drone_{drone_id}"
            action = row.get(action_key)

            if action:
                logger.info(f"Drone {drone_id} will perform: {action}")
                t = threading.Thread(target=drone.run_action, args=(action, stop_event))
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
        logger.info("All robot and drone actions completed successfully.")

    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error executing robot and drone actions: {e}")
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
    drones = initialize_drones(action_name_to_time, action_name_to_repeat_time)

    if SIMULATOR_BASE_URL is None:
        # Play the song before starting robot actions
        play_song(song_file_path)
    # Notify the simulator to change the video source before starting robot actions
    else:
        play_song_in_simulator(song)

    for row in robot_actions:
        logger.info(f"Processing row: {row}")
        try:
            execute_robot_actions(robots, drones, row, stop_event)
            if stop_event.is_set():
                logger.info("Stop event detected in main loop. Exiting...")
                return
        except KeyboardInterrupt:
            logger.info("Main loop interrupted by user (Ctrl+C). Exiting...")
            stop_event.set()
            return
    if SIMULATOR_BASE_URL is None:
        stop_song()


def play_song_in_simulator(song):
    try:
        response = requests.post(
            f"{SIMULATOR_BASE_URL}/api/video/change_source?session_key={SESSION_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "video_src": f"https://storage.googleapis.com/{SONG_BUCKET}/{song}.mp4"
            },
            timeout=3,
        )
        if response.status_code == 200:
            logger.info(f"Simulator video source changed successfully for {song}.")
        else:
            logger.warning(
                f"Failed to change simulator video source: {response.status_code} {response.text}"
            )
    except requests.RequestException as e:
        logger.error(f"Error calling simulator API: {e}")


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
