import logging
import os
import threading
import time
from typing import Dict

import requests

from action import RobotAction
from action_compiler import ActionCompiler
from constant import (
    DRONE_REAL_HOSTS,
    DRONE_SIMULATOR,
    DRONE_SIMULATOR_IP,
    DRONE_SIMULATOR_PORTS,
    ROBOT_IPS,
    SESSION_KEY,
    SIMULATOR_BASE_URL,
    SKIP_DRONES,
    SONG_BASE_URL,
)
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


def initialize_drones(
    action_name_to_time: Dict, action_name_to_repeat_time: Dict
) -> Dict[int, DroneAction]:
    """Initialize all drones and return them as a dictionary."""
    
    drones = {}
    tello_instances = []
    
    if DRONE_SIMULATOR:
        # For simulator, use the predefined ports (limited to 2 drones)
        simulator_drones = ["drone1", "drone2"]
        for i, drone_key in enumerate(simulator_drones):
            if i >= len(DRONE_REAL_HOSTS):  # Don't exceed the number of configured hosts
                break
            tello = Tello(
                host=DRONE_SIMULATOR_IP,
                control_udp=DRONE_SIMULATOR_PORTS[drone_key]["control_udp"],
                state_udp=DRONE_SIMULATOR_PORTS[drone_key]["state_udp"],
            )
            tello_instances.append(tello)
    else:
        # Real drones - create based on DRONE_REAL_HOSTS length
        for host in DRONE_REAL_HOSTS:
            tello = Tello(host=host)
            tello_instances.append(tello)
    
    # Connect all drones
    for i, tello in enumerate(tello_instances):
        try:
            tello.connect()
            logger.info(f"Drone {i+1} connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to drone {i+1}: {e}")
            continue

    # Create DroneAction instances
    for i, tello in enumerate(tello_instances):
        drone_id = i + 1
        drone_action = DroneAction(
            tello,
            action_name_to_time,
            action_name_to_repeat_time,
            f"drone_{drone_id}",
        )
        drones[drone_id] = drone_action
        logger.info(f"Drone {drone_id} initialized")

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
        if not drones:
            logger.info("No drones initialized, skipping drone actions.")
            # You can return here if you want to skip the rest, or just continue
        else:
            for drone_id, drone in drones.items():
                action_key = f"Drone_{drone_id}"
                action = row.get(action_key)

                if action:
                    logger.info(f"Drone {drone_id} will perform: {action}")
                    t = threading.Thread(
                        target=drone.run_action, args=(action, stop_event)
                    )
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
    if SKIP_DRONES:
        drones = []
    else:
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
            json={"video_src": f"{SONG_BASE_URL}/{song}.mp4"},
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
