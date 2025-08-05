"""
Updated drone_action.py implementing BaseAction.
"""

import threading
import time
from typing import Dict, Optional

from actions.base_action import BaseAction


class DroneAction(BaseAction):
    """Updated drone action handler implementing BaseAction interface."""

    def __init__(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Optional[Dict[str, int]] = None,
        drone=None,
        drone_id: str = "drone_1",
    ):
        super().__init__(drone_id, action_name_to_time, action_name_to_repeat_time)
        self.tello = drone
        self.drone_id = drone_id
        if not self.tello:
            self._initialize_drone()

    def _initialize_drone(self):
        """Initialize drone connection."""
        try:
            from driver.djitellopy import Tello

            self.tello = Tello()
            self.tello.connect()
            self.logger.info("Drone connected successfully")
        except ImportError:
            self.logger.warning("djitellopy not available, using simulation mode")
        except Exception as e:
            self.logger.error(f"Failed to connect to drone: {e}")

    def _execute_single_action(
        self, action_name: str, stop_event: Optional[threading.Event] = None
    ) -> bool:
        """Execute a single drone action."""
        action_time = self.get_action_time(action_name)
        repeat_count = self.get_repeat_count(action_name)

        # If action not found in spreadsheet, use default timing like original version
        if action_time <= 0:
            action_time = self._get_default_action_time(action_name)
            self.logger.info(f"Using default timing for drone action '{action_name}': {action_time}s")

        self.logger.info(
            f"Executing drone action '{action_name}' for {action_time}s, {repeat_count} times"
        )

        for i in range(repeat_count):
            if stop_event and stop_event.is_set():
                return False

            try:
                success = self._execute_drone_command(action_name, action_time)
                if not success:
                    return False

                self.logger.info(
                    f"Completed drone action '{action_name}' iteration {i + 1}/{repeat_count}"
                )

            except Exception as e:
                self.logger.error(f"Error executing drone action '{action_name}': {e}")
                return False

        return True

    def _get_default_action_time(self, action_name: str) -> float:
        """
        Get default timing for drone actions that aren't in the actions dictionary.
        Based on original drone_action.py implementation.
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

    def _execute_drone_command(self, action_name: str, duration: float) -> bool:
        """Execute specific drone command."""
        if not self.tello:
            # Simulation mode
            self.logger.info(f"Simulating drone action: {action_name}")
            time.sleep(duration)
            return True

        try:
            # Map action names to drone commands - handle parameterized commands like original
            action_name_lower = action_name.lower()
            
            if action_name_lower == "takeoff":
                self.tello.takeoff()
            elif action_name_lower == "land":
                self.tello.land()
            elif action_name_lower.startswith("move_up"):
                distance = self._extract_distance(action_name_lower, 100)
                self.tello.move_up(distance)
                self.logger.info(f"Drone: Move up {distance}cm executed")
            elif action_name_lower.startswith("move_down"):
                distance = self._extract_distance(action_name_lower, 100)
                self.tello.move_down(distance)
                self.logger.info(f"Drone: Move down {distance}cm executed")
            elif action_name_lower.startswith("move_left"):
                distance = self._extract_distance(action_name_lower, 100)
                self.tello.move_left(distance)
                self.logger.info(f"Drone: Move left {distance}cm executed")
            elif action_name_lower.startswith("move_right"):
                distance = self._extract_distance(action_name_lower, 100)
                self.tello.move_right(distance)
                self.logger.info(f"Drone: Move right {distance}cm executed")
            elif action_name_lower.startswith("move_forward"):
                distance = self._extract_distance(action_name_lower, 100)
                self.tello.move_forward(distance)
                self.logger.info(f"Drone: Move forward {distance}cm executed")
            elif action_name_lower.startswith("move_back"):
                distance = self._extract_distance(action_name_lower, 100)
                self.tello.move_back(distance)
                self.logger.info(f"Drone: Move back {distance}cm executed")
            elif action_name_lower.startswith("rotate_cw"):
                angle = self._extract_angle(action_name_lower, 90)
                self.tello.rotate_clockwise(angle)
                self.logger.info(f"Drone: Rotate clockwise {angle}° executed")
            elif action_name_lower.startswith("rotate_ccw"):
                angle = self._extract_angle(action_name_lower, 90)
                self.tello.rotate_counter_clockwise(angle)
                self.logger.info(f"Drone: Rotate counter-clockwise {angle}° executed")
            elif action_name_lower.startswith("curve"):
                # Parse curve command: curve_x1_y1_z1_x2_y2_z2_speed
                params = self._parse_command(action_name_lower, "curve")
                if params and len(params) >= 7:
                    x1, y1, z1, x2, y2, z2, speed = params[:7]
                    self.tello.curve_xyz_speed(x1, y1, z1, x2, y2, z2, speed)
                    self.logger.info(f"Drone: Curve from ({x1}, {y1}, {z1}) to ({x2}, {y2}, {z2}) at speed {speed}cm/s executed")
                else:
                    self.logger.error(f"Failed to parse curve command: {action_name}")
                    return False
            elif action_name_lower.startswith("go"):
                # Parse go command: go_x_y_z_speed
                params = self._parse_command(action_name_lower, "go")
                if params and len(params) >= 4:
                    x, y, z, speed = params[:4]
                    self.tello.go_xyz_speed(x, y, z, speed)
                    self.logger.info(f"Drone: Go to ({x}, {y}, {z}) at speed {speed}cm/s executed")
                else:
                    self.logger.error(f"Failed to parse go command: {action_name}")
                    return False
            elif action_name_lower == "up":
                self.tello.move_up(int(duration * 20))  # 20cm per second
            elif action_name_lower == "down":
                self.tello.move_down(int(duration * 20))
            elif action_name_lower == "left":
                self.tello.move_left(int(duration * 20))
            elif action_name_lower == "right":
                self.tello.move_right(int(duration * 20))
            elif action_name_lower == "forward":
                self.tello.move_forward(int(duration * 20))
            elif action_name_lower == "back":
                self.tello.move_back(int(duration * 20))
            elif action_name_lower == "rotate_clockwise":
                self.tello.rotate_clockwise(int(duration * 90))  # 90 degrees per second
            elif action_name_lower == "rotate_counter_clockwise":
                self.tello.rotate_counter_clockwise(int(duration * 90))
            elif action_name_lower == "flip_forward":
                self.tello.flip_forward()
            elif action_name_lower == "flip_back":
                self.tello.flip_back()
            elif action_name_lower == "flip_left":
                self.tello.flip_left()
            elif action_name_lower == "flip_right":
                self.tello.flip_right()
            else:
                self.logger.warning(f"Unknown drone action: {action_name}")
                time.sleep(duration)
                return True

            # Wait for the action to complete
            time.sleep(duration)
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute drone command '{action_name}': {e}")
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

    def cleanup(self) -> None:
        """Clean up drone resources."""
        if self.tello:
            try:
                self.tello.land()
                self.tello.end()
                self.logger.info("Drone disconnected successfully")
            except Exception as e:
                self.logger.error(f"Error during drone cleanup: {e}")
        self.logger.info("Cleaning up drone action handler")
