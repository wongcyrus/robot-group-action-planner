import logging
import threading
import time
from typing import Dict

from djitellopy import Tello


class DroneAction:
    """
    Handles drone action operations for DJI Tello drones.
    Provides an interface to execute drone actions like takeoff, land, move, etc.
    """

    def __init__(
        self,
        drone: Tello,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int] = None,
        drone_id: str = "drone_1",
    ):
        """
        Initialize the DroneAction class.

        Args:
            drone: The Tello drone instance
            action_name_to_time: Dictionary mapping action names to their execution time
            action_name_to_repeat_time: Dictionary mapping action names to their repeat time
            drone_id: The ID of the drone
        """
        self.drone = drone
        self.drone_id = drone_id
        self.actions = action_name_to_time
        self.repeat_actions = action_name_to_repeat_time or {}
        self.logger = logging.getLogger("DroneAction")

    def run_action(self, name: str, stop_event: threading.Event = None) -> bool:
        """
        Run one or more drone actions (multi-line supported).

        Args:
            name: Action name(s), possibly multi-line.
            stop_event: Optional threading.Event for interruption.

        Returns:
            True if actions were executed successfully, False otherwise.
        """
        # Handle single or multi-line names: split by newlines if present, else use as single action
        if "\n" in name:
            names = [n.strip() for n in name.splitlines() if n.strip()]
        else:
            names = [name.strip()] if name.strip() else []

        for n in names:
            if stop_event is not None and stop_event.is_set():
                self.logger.info("Drone action interrupted by stop_event.")
                break

            # Get timing information - use default if not found in actions dictionary
            if n in self.actions:
                sleep_time = self.actions[n]
                repeat = self.repeat_actions.get(n, 1)
            else:
                # Use default timing for drone actions not in spreadsheet
                sleep_time = self._get_default_action_time(n)
                repeat = 1
                self.logger.info(
                    f"Using default timing for drone action '{n}': {sleep_time}s"
                )

            # Execute the drone action multiple times if needed
            for _ in range(repeat):
                if stop_event is not None and stop_event.is_set():
                    self.logger.info(
                        "Drone action interrupted by stop_event during repeat."
                    )
                    break

                success = self._execute_drone_command(n)
                if not success:
                    self.logger.error(f"Failed to execute drone action: {n}")
                    return False

                # Small delay between repeats
                if repeat > 1:
                    time.sleep(0.1)

            # Wait for the specified time
            waited = 0.0
            interval = 0.1
            while waited < float(sleep_time):
                if stop_event is not None and stop_event.is_set():
                    self.logger.info(
                        "Drone action interrupted by stop_event during sleep."
                    )
                    break
                time.sleep(interval)
                waited += interval

        return True

    def _execute_drone_command(self, action_name: str) -> bool:
        """
        Execute a specific drone command based on the action name.

        Args:
            action_name: The name of the action to execute

        Returns:
            True if command was executed successfully, False otherwise.
        """
        try:
            # Map action names to drone commands
            action_name_lower = action_name.lower()

            if action_name_lower == "takeoff":
                self.drone.takeoff()
                self.logger.info(f"Drone {self.drone_id}: Takeoff executed")

            elif action_name_lower == "land":
                self.drone.land()
                self.logger.info(f"Drone {self.drone_id}: Land executed")

            elif action_name_lower.startswith("move_up"):
                # Extract distance if provided, default to 20cm
                distance = self._extract_distance(action_name_lower, 100)
                self.drone.move_up(distance)
                self.logger.info(
                    f"Drone {self.drone_id}: Move up {distance}cm executed"
                )

            elif action_name_lower.startswith("move_down"):
                distance = self._extract_distance(action_name_lower, 100)
                self.drone.move_down(distance)
                self.logger.info(
                    f"Drone {self.drone_id}: Move down {distance}cm executed"
                )

            elif action_name_lower.startswith("move_left"):
                distance = self._extract_distance(action_name_lower, 100)
                self.drone.move_left(distance)
                self.logger.info(
                    f"Drone {self.drone_id}: Move left {distance}cm executed"
                )

            elif action_name_lower.startswith("move_right"):
                distance = self._extract_distance(action_name_lower, 100)
                self.drone.move_right(distance)
                self.logger.info(
                    f"Drone {self.drone_id}: Move right {distance}cm executed"
                )

            elif action_name_lower.startswith("move_forward"):
                distance = self._extract_distance(action_name_lower, 100)
                self.drone.move_forward(distance)
                self.logger.info(
                    f"Drone {self.drone_id}: Move forward {distance}cm executed"
                )

            elif action_name_lower.startswith("move_back"):
                distance = self._extract_distance(action_name_lower, 100)
                self.drone.move_back(distance)
                self.logger.info(
                    f"Drone {self.drone_id}: Move back {distance}cm executed"
                )

            elif action_name_lower.startswith("rotate_cw"):
                angle = self._extract_angle(action_name_lower, 90)
                self.drone.rotate_clockwise(angle)
                self.logger.info(
                    f"Drone {self.drone_id}: Rotate clockwise {angle}° executed"
                )

            elif action_name_lower.startswith("rotate_ccw"):
                angle = self._extract_angle(action_name_lower, 90)
                self.drone.rotate_counter_clockwise(angle)
                self.logger.info(
                    f"Drone {self.drone_id}: Rotate counter-clockwise {angle}° executed"
                )

            elif action_name_lower == "flip_f":
                self.drone.flip_forward()
                self.logger.info(f"Drone {self.drone_id}: Flip forward executed")

            elif action_name_lower == "flip_b":
                self.drone.flip_back()
                self.logger.info(f"Drone {self.drone_id}: Flip back executed")

            elif action_name_lower == "flip_l":
                self.drone.flip_left()
                self.logger.info(f"Drone {self.drone_id}: Flip left executed")

            elif action_name_lower == "flip_r":
                self.drone.flip_right()
                self.logger.info(f"Drone {self.drone_id}: Flip right executed")

            elif action_name_lower == "hover":
                # Hover is essentially doing nothing for the specified time
                self.logger.info(f"Drone {self.drone_id}: Hover executed")

            else:
                self.logger.warning(f"Unknown drone action: {action_name}")
                return False

            return True

        except (ConnectionError, OSError, ValueError) as e:
            self.logger.error(f"Error executing drone command '{action_name}': {e}")
            return False

    def _extract_distance(self, action_name: str, default_distance: int) -> int:
        """Extract distance from action name like 'move_up_50' -> 50"""
        parts = action_name.split("_")
        if len(parts) >= 3 and parts[2].isdigit():
            return int(parts[2])
        return default_distance

    def _extract_angle(self, action_name: str, default_angle: int) -> int:
        """Extract angle from action name like 'rotate_cw_90' -> 90"""
        parts = action_name.split("_")
        if len(parts) >= 3 and parts[2].isdigit():
            return int(parts[2])
        return default_angle

    def _get_default_action_time(self, action_name: str) -> float:
        """
        Get default timing for drone actions that aren't in the actions dictionary.

        Args:
            action_name: The name of the drone action

        Returns:
            Default time in seconds for the action
        """
        action_name_lower = action_name.lower()

        # Define default timings for different types of drone actions
        if action_name_lower in ["takeoff", "land"]:
            return 2.0  # Takeoff and landing take a bit longer
        elif action_name_lower.startswith("move_"):
            return 2.0  # Movement actions
        elif action_name_lower.startswith("rotate_"):
            return 2.0  # Rotation actions
        elif action_name_lower.startswith("flip_"):
            return 2.0  # Flip actions
        elif action_name_lower == "hover":
            return 2.0  # Hover action
        else:
            return 2.0  # Default for unknown actions

    def emergency_stop(self):
        """Emergency stop the drone."""
        try:
            self.drone.emergency()
            self.logger.info(f"Drone {self.drone_id}: Emergency stop executed")
        except (ConnectionError, OSError, ValueError) as e:
            self.logger.error(f"Error executing emergency stop: {e}")
