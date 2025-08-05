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
            from djitellopy import Tello

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

        if action_time <= 0:
            self.logger.warning(
                f"Drone action '{action_name}' not found or has invalid time"
            )
            return False

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

    def _execute_drone_command(self, action_name: str, duration: float) -> bool:
        """Execute specific drone command."""
        if not self.tello:
            # Simulation mode
            self.logger.info(f"Simulating drone action: {action_name}")
            time.sleep(duration)
            return True

        try:
            # Map action names to drone commands
            if action_name == "takeoff":
                self.tello.takeoff()
            elif action_name == "land":
                self.tello.land()
            elif action_name == "up":
                self.tello.move_up(int(duration * 20))  # 20cm per second
            elif action_name == "down":
                self.tello.move_down(int(duration * 20))
            elif action_name == "left":
                self.tello.move_left(int(duration * 20))
            elif action_name == "right":
                self.tello.move_right(int(duration * 20))
            elif action_name == "forward":
                self.tello.move_forward(int(duration * 20))
            elif action_name == "back":
                self.tello.move_back(int(duration * 20))
            elif action_name == "rotate_clockwise":
                self.tello.rotate_clockwise(int(duration * 90))  # 90 degrees per second
            elif action_name == "rotate_counter_clockwise":
                self.tello.rotate_counter_clockwise(int(duration * 90))
            elif action_name == "flip_forward":
                self.tello.flip_forward()
            elif action_name == "flip_back":
                self.tello.flip_back()
            elif action_name == "flip_left":
                self.tello.flip_left()
            elif action_name == "flip_right":
                self.tello.flip_right()
            else:
                self.logger.warning(f"Unknown drone action: {action_name}")
                time.sleep(duration)

            return True

        except Exception as e:
            self.logger.error(f"Failed to execute drone command '{action_name}': {e}")
            return False

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
