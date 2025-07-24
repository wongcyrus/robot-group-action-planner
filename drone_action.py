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
            threads = []
            def action_thread():
                if stop_event is not None and stop_event.is_set():
                    self.logger.info(
                        "Drone action interrupted by stop_event during repeat."
                    )
                    return
                success = self._execute_drone_command(n)
                if not success:
                    self.logger.error(f"Failed to execute drone action: {n}")

            for _ in range(repeat):
                t = threading.Thread(target=action_thread)
                t.start()
                threads.append(t)
                if repeat > 1:
                    time.sleep(0.1)

            for t in threads:
                t.join()

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
                self.drone.set_speed(100)  # Set a reasonable speed for takeoff
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

            elif action_name_lower.startswith("go"):
                # Parse go command: go_x_y_z_speed or go_x_y_z_speed_mid
                params = self._parse_command(action_name_lower, "go")
                if params:
                    if len(params) == 4:  # go_x_y_z_speed
                        x, y, z, speed = params
                        self.drone.go_xyz_speed(x, y, z, speed)
                        self.logger.info(
                            f"Drone {self.drone_id}: Go to ({x}, {y}, {z}) at speed {speed}cm/s executed"
                        )
                    elif len(params) == 5:  # go_x_y_z_speed_mid
                        x, y, z, speed, mid = params
                        self.drone.go_xyz_speed_mid(x, y, z, speed, mid)
                        self.logger.info(
                            f"Drone {self.drone_id}: Go to ({x}, {y}, {z}) relative to pad {mid} at speed {speed}cm/s executed"
                        )
                    else:
                        self.logger.error(f"Invalid go parameters: {action_name}")
                        return False
                else:
                    self.logger.error(f"Failed to parse go command: {action_name}")
                    return False

            elif action_name_lower.startswith("curve"):
                # Parse curve command: curve_x1_y1_z1_x2_y2_z2_speed or curve_x1_y1_z1_x2_y2_z2_speed_mid
                params = self._parse_command(action_name_lower, "curve")
                if params:
                    if len(params) == 7:  # curve_x1_y1_z1_x2_y2_z2_speed
                        x1, y1, z1, x2, y2, z2, speed = params
                        self.drone.curve_xyz_speed(x1, y1, z1, x2, y2, z2, speed)
                        self.logger.info(
                            f"Drone {self.drone_id}: Curve from ({x1}, {y1}, {z1}) to ({x2}, {y2}, {z2}) at speed {speed}cm/s executed"
                        )
                    elif len(params) == 8:  # curve_x1_y1_z1_x2_y2_z2_speed_mid
                        x1, y1, z1, x2, y2, z2, speed, mid = params
                        self.drone.curve_xyz_speed_mid(x1, y1, z1, x2, y2, z2, speed, mid)
                        self.logger.info(
                            f"Drone {self.drone_id}: Curve from ({x1}, {y1}, {z1}) to ({x2}, {y2}, {z2}) relative to pad {mid} at speed {speed}cm/s executed"
                        )
                    else:
                        self.logger.error(f"Invalid curve parameters: {action_name}")
                        return False
                else:
                    self.logger.error(f"Failed to parse curve command: {action_name}")
                    return False

            elif action_name_lower.startswith("jump"):
                # Parse jump command: jump_x_y_z_speed_yaw_mid1_mid2
                params = self._parse_command(action_name_lower, "jump")
                if params and len(params) == 7:
                    x, y, z, speed, yaw, mid1, mid2 = params
                    self.drone.go_xyz_speed_yaw_mid(x, y, z, speed, yaw, mid1, mid2)
                    self.logger.info(
                        f"Drone {self.drone_id}: Jump to ({x}, {y}, {z}) with yaw {yaw}° from pad {mid1} to pad {mid2} at speed {speed}cm/s executed"
                    )
                else:
                    self.logger.error(f"Failed to parse jump command: {action_name}")
                    return False

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

    def _parse_command(self, action_name: str, command_prefix: str) -> list:
        """
        Parse commands with multiple parameters.
        
        Examples:
        - go_100_50_-20_30 -> [100, 50, -20, 30]
        - curve_50_0_20_100_0_40_25 -> [50, 0, 20, 100, 0, 40, 25]
        - jump_100_50_20_30_90_1_2 -> [100, 50, 20, 30, 90, 1, 2]
        
        Args:
            action_name: The action name to parse
            command_prefix: The command prefix to remove (e.g., "go", "curve")
            
        Returns:
            List of integer parameters, or None if parsing fails
        """
        try:
            # Remove the command prefix
            if not action_name.startswith(command_prefix):
                return None
                
            # Extract the parameter part
            param_part = action_name[len(command_prefix):]
            if not param_part.startswith("_"):
                return None
                
            # Split by underscore and convert to integers
            param_strings = param_part[1:].split("_")
            
            # Convert all parameters to integers, handling negative numbers
            params = []
            for param_str in param_strings:
                if param_str.lstrip("-").isdigit():
                    params.append(int(param_str))
                else:
                    return None
                    
            return params
            
        except (ValueError, IndexError):
            return None

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
            return 3.0  # Takeoff and landing take a bit longer
        elif action_name_lower.startswith("move_"):
            return 3.0  # Movement actions
        elif action_name_lower.startswith("rotate_"):
            return 3.0  # Rotation actions
        elif action_name_lower.startswith("flip_"):
            return 4.0  # Flip actions
        elif action_name_lower == "hover":
            return 4.0  # Hover action
        elif action_name_lower.startswith("go"):
            return 3.0  # XYZ movement actions take longer
        elif action_name_lower.startswith("curve"):
            return 7.0  # Curve movements take longer
        elif action_name_lower.startswith("jump"):
            return 5.0  # Jump actions
        else:
            return 5.0  # Default for unknown actions

    def emergency_stop(self):
        """Emergency stop the drone."""
        try:
            self.drone.emergency()
            self.logger.info(f"Drone {self.drone_id}: Emergency stop executed")
        except (ConnectionError, OSError, ValueError) as e:
            self.logger.error(f"Error executing emergency stop: {e}")
