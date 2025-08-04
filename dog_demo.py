#!/usr/bin/env python3
"""
Example script demonstrating the use of 2 robot dogs with the DogAction class.

This script shows how to:
1. Initialize multiple dog robots
2. Execute coordinated actions across both dogs
3. Handle timing and synchronization
"""

import logging
import threading
import time
from typing import Dict

from dog.action_executor import DogActionExecutor
from dog_action import DogAction

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dog robot configuration
DOG_CONFIGS = [
    {"ip": "192.168.137.41", "port": 8830, "name": "dog_1"},
    {"ip": "192.168.137.42", "port": 8830, "name": "dog_2"},
]


def create_sample_action_mappings():
    """Create sample action mappings for demonstration."""
    action_name_to_time = {
        "activate": 1.0,
        "stand_up": 2.0,
        "forward": 2.0,
        "back": 2.0,
        "left": 2.0,
        "right": 2.0,
        "cw": 2.0,
        "ccw": 2.0,
        "hop": 1.5,
        "lay_down": 2.0,
        "stop": 0.5,
        "deactivate": 1.0,
    }

    action_name_to_repeat_time = {
        "hop": 2,  # Hop twice
        "forward": 1,  # Move forward once
    }

    return action_name_to_time, action_name_to_repeat_time


def initialize_dogs() -> Dict[int, DogAction]:
    """Initialize dog robots and return them as a dictionary."""
    dogs = {}
    action_name_to_time, action_name_to_repeat_time = create_sample_action_mappings()

    for idx, config in enumerate(DOG_CONFIGS):
        dog_id = idx + 1
        try:
            # Create DogActionExecutor instance
            dog_executor = DogActionExecutor(
                robot_name=config["name"],
                robot_ip=config["ip"],
                robot_port=config["port"],
            )

            # Create DogAction wrapper
            dog_action = DogAction(
                dog_executor,
                action_name_to_time,
                action_name_to_repeat_time,
                config["name"],
            )
            dogs[dog_id] = dog_action
            logger.info(
                f"Dog {dog_id} ({config['name']}) initialized at {config['ip']}:{config['port']}"
            )
        except (ConnectionError, OSError, ValueError) as e:
            logger.error(f"Failed to initialize Dog {dog_id}: {e}")

    return dogs


def demo_synchronized_actions(dogs: Dict[int, DogAction]):
    """Demonstrate synchronized actions across multiple dogs."""
    logger.info("Starting synchronized dog actions demo...")

    stop_event = threading.Event()

    # Demo sequence: both dogs perform the same actions simultaneously
    demo_sequence = [
        ("activate", "Activating both dogs"),
        ("stand_up", "Both dogs standing up"),
        ("forward_100", "Both dogs moving forward"),
        ("cw_90", "Both dogs rotating clockwise"),
        ("hop", "Both dogs hopping"),
        ("back_50", "Both dogs moving back"),
        ("lay_down", "Both dogs laying down"),
        ("deactivate", "Deactivating both dogs"),
    ]

    for action, description in demo_sequence:
        logger.info(f"Demo step: {description}")

        # Create threads for simultaneous execution
        threads = []
        for dog_id, dog in dogs.items():
            thread = threading.Thread(
                target=dog.run_action,
                args=(action, stop_event),
                name=f"Dog{dog_id}Thread",
            )
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Brief pause between actions
        time.sleep(1)

        if stop_event.is_set():
            logger.info("Demo interrupted by stop event")
            break


def demo_alternating_actions(dogs: Dict[int, DogAction]):
    """Demonstrate alternating actions between dogs."""
    logger.info("Starting alternating dog actions demo...")

    stop_event = threading.Event()

    # Demo sequence: dogs take turns performing actions
    demo_sequence = [
        (1, "forward_50", "Dog 1 moving forward"),
        (2, "forward_50", "Dog 2 moving forward"),
        (1, "cw_45", "Dog 1 rotating clockwise"),
        (2, "ccw_45", "Dog 2 rotating counter-clockwise"),
        (1, "hop", "Dog 1 hopping"),
        (2, "hop", "Dog 2 hopping"),
        (1, "back_50", "Dog 1 moving back"),
        (2, "back_50", "Dog 2 moving back"),
    ]

    for dog_id, action, description in demo_sequence:
        if dog_id in dogs:
            logger.info(f"Demo step: {description}")
            dogs[dog_id].run_action(action, stop_event)
            time.sleep(0.5)  # Brief pause between actions

        if stop_event.is_set():
            logger.info("Demo interrupted by stop event")
            break


def demo_coordinated_dance(dogs: Dict[int, DogAction]):
    """Demonstrate a coordinated dance routine."""
    logger.info("Starting coordinated dance demo...")

    stop_event = threading.Event()

    # Dance routine with different actions for each dog
    dance_moves = [
        {1: "stand_up", 2: "stand_up"},
        {1: "left_30", 2: "right_30"},
        {1: "right_60", 2: "left_60"},
        {1: "left_30", 2: "right_30"},
        {1: "hop", 2: "hop"},
        {1: "cw_180", 2: "ccw_180"},
        {1: "forward_30", 2: "forward_30"},
        {1: "back_30", 2: "back_30"},
        {1: "lay_down", 2: "lay_down"},
    ]

    for move_set in dance_moves:
        logger.info(f"Dance move: {move_set}")

        # Create threads for simultaneous execution
        threads = []
        for dog_id, action in move_set.items():
            if dog_id in dogs:
                thread = threading.Thread(
                    target=dogs[dog_id].run_action,
                    args=(action, stop_event),
                    name=f"Dog{dog_id}DanceThread",
                )
                threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Brief pause between dance moves
        time.sleep(0.5)

        if stop_event.is_set():
            logger.info("Dance interrupted by stop event")
            break


def get_dogs_status(dogs: Dict[int, DogAction]):
    """Display status of all dogs."""
    logger.info("=== Dog Status Report ===")
    for dog_id, dog in dogs.items():
        status = dog.get_status()
        logger.info(f"Dog {dog_id}: {status}")


def main():
    """Main function to demonstrate dog robot functionality."""
    try:
        # Initialize dogs
        dogs = initialize_dogs()

        if not dogs:
            logger.error("No dogs initialized. Check your configuration and network.")
            return

        logger.info(f"Successfully initialized {len(dogs)} dog robots")

        # Get initial status
        get_dogs_status(dogs)

        # Run different demo scenarios
        demo_synchronized_actions(dogs)

        time.sleep(2)  # Pause between demos

        demo_alternating_actions(dogs)

        time.sleep(2)  # Pause between demos

        demo_coordinated_dance(dogs)

        # Final status check
        get_dogs_status(dogs)

        logger.info("Dog demo completed successfully!")

    except KeyboardInterrupt:
        logger.info("Demo interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Error during demo: {e}")
    finally:
        # Emergency stop all dogs if needed
        if "dogs" in locals():
            for dog_id, dog in dogs.items():
                try:
                    dog.emergency_stop()
                    logger.info(f"Emergency stop sent to Dog {dog_id}")
                except Exception as e:
                    logger.error(f"Error stopping Dog {dog_id}: {e}")


if __name__ == "__main__":
    main()
