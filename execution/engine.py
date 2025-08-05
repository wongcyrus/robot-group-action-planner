"""
Execution engine for robot actions.
"""

import logging
import threading
from typing import Any, Dict, List


class ExecutionEngine:
    """Handles execution of robot action sequences."""

    def __init__(self):
        """Initialize execution engine."""
        self.logger = logging.getLogger("ExecutionEngine")

    def execute_action_sequence(
        self,
        robots: Dict[str, List[Any]],
        robot_actions: List[Dict[str, Any]],
        stop_event: threading.Event,
    ) -> bool:
        """Execute a sequence of robot actions."""
        try:
            self.logger.info(f"Starting execution of {len(robot_actions)} actions")

            for i, action in enumerate(robot_actions):
                if stop_event.is_set():
                    self.logger.info("Stop event detected, aborting execution")
                    return False

                self.logger.info(
                    f"Executing action {i+1}/{len(robot_actions)}: {action}"
                )

                success = self._execute_single_action(robots, action, stop_event)
                if not success:
                    self.logger.error(f"Failed to execute action {i+1}")
                    return False

            self.logger.info("All actions executed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error in action execution: {e}")
            return False

    def _execute_single_action(
        self,
        robots: Dict[str, List[Any]],
        action: Dict[str, Any],
        stop_event: threading.Event,
    ) -> bool:
        """Execute a single action across all robot types."""
        threads = []
        results = []

        try:
            # Start action threads for each robot type
            for robot_type, robot_list in robots.items():
                if robot_type in action:
                    action_name = action[robot_type]

                    for robot in robot_list:
                        if stop_event.is_set():
                            return False

                        thread = threading.Thread(
                            target=self._robot_action_wrapper,
                            args=(robot, action_name, stop_event, results),
                        )
                        threads.append(thread)
                        thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check if all actions succeeded
            return all(results)

        except Exception as e:
            self.logger.error(f"Error executing single action: {e}")
            return False

    def _robot_action_wrapper(
        self,
        robot: Any,
        action_name: str,
        stop_event: threading.Event,
        results: List[bool],
    ) -> None:
        """Wrapper for robot action execution in thread."""
        try:
            success = robot.run_action(action_name, stop_event)
            results.append(success)

        except Exception as e:
            self.logger.error(f"Robot action failed: {e}")
            results.append(False)

    def cleanup_all_robots(self, robots: Dict[str, List[Any]]) -> None:
        """Clean up all robot resources."""
        try:
            for robot_type, robot_list in robots.items():
                self.logger.info(f"Cleaning up {len(robot_list)} {robot_type}")

                for robot in robot_list:
                    try:
                        robot.cleanup()
                    except Exception as e:
                        self.logger.error(f"Error cleaning up robot: {e}")

        except Exception as e:
            self.logger.error(f"Error in robot cleanup: {e}")
