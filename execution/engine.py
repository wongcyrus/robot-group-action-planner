"""
Execution engine for robot actions.
"""

import logging
import threading
import time
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

                success = self._execute_single_step(robots, action, stop_event)
                if not success:
                    self.logger.warning(
                        f"Some actions failed in sequence {i+1}, but continuing with next sequence"
                    )
                    # Continue with next action sequence instead of stopping entirely

            self.logger.info("All actions executed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error in action execution: {e}")
            return False

    def _execute_single_step(
        self,
        robots: Dict[str, List[Any]],
        action: Dict[str, Any],
        stop_event: threading.Event,
    ) -> bool:
        """Execute a single action across all robot types."""
        threads = []
        results = []

        try:
            # Get the time value from the action (this is critical for scheduling!)
            time_value = action.get("Time")
            if time_value:
                self.logger.info(f"Executing actions with time value: {time_value}")
            else:
                self.logger.warning(
                    "No time value found in action, using default 1 second"
                )
                time_value = "1"

            # Start action threads for each robot type
            for robot_type, robot_list in robots.items():
                # Map robot_type to the expected column prefix in the action data
                if robot_type == "robots":
                    column_prefix = "Humanoid_"
                elif robot_type == "drones":
                    column_prefix = "Drone_"
                elif robot_type == "dogs":
                    column_prefix = "Dog_"
                else:
                    continue  # Skip unknown robot types

                # Find matching columns for this robot type
                robot_actions_found = False
                for robot_index, robot in enumerate(robot_list, 1):
                    action_key = f"{column_prefix}{robot_index}"
                    action_name = action.get(action_key)

                    if action_name:  # Only process if action is not empty
                        robot_actions_found = True
                        self.logger.info(f"{action_key} will perform: {action_name}")

                        if stop_event.is_set():
                            return False

                        thread = threading.Thread(
                            target=self._robot_action_wrapper,
                            args=(robot, action_name, stop_event, results),
                        )
                        threads.append(thread)
                        thread.start()

                if not robot_actions_found:
                    self.logger.debug(f"No actions found for robot type: {robot_type}")

            # Wait for the specified time duration (this was missing in the refactored version!)
            self.logger.info(f"Waiting for {time_value} seconds")

            # Start timing for the minimum duration enforcement
            start_time = time.time()
            max_wait_time = float(time_value)

            # Wait for all threads to complete - let them run for their full action time
            # The real timeout protection happens at the individual action level (drone commands, HTTP requests)
            self.logger.info("Waiting for all robot actions to complete...")

            for i, thread in enumerate(threads):
                thread_wait_start = time.time()
                while thread.is_alive():
                    # Check every 0.5 seconds instead of blocking indefinitely
                    thread.join(timeout=0.5)
                    if stop_event.is_set():
                        self.logger.info("Stop event set, breaking join loop.")
                        break

                    # Log if a thread is taking longer than the planned time (for monitoring)
                    thread_elapsed = time.time() - thread_wait_start
                    if thread_elapsed > max_wait_time + 2:  # 2 second grace period
                        self.logger.warning(
                            f"Thread {i+1}/{len(threads)} has been running for {thread_elapsed:.1f}s "
                            f"(planned action time: {time_value}s) - may indicate blocking issue"
                        )

                # Log when each thread completes
                thread_duration = time.time() - thread_wait_start
                self.logger.debug(
                    f"Thread {i+1}/{len(threads)} completed in {thread_duration:.2f}s"
                )

            # Ensure we wait for the full time duration even if threads complete early
            elapsed_time = time.time() - start_time
            if elapsed_time < max_wait_time and not stop_event.is_set():
                remaining_sleep = max_wait_time - elapsed_time
                self.logger.info(
                    f"Robot actions completed early, waiting additional {remaining_sleep:.2f} "
                    f"seconds to reach planned duration of {time_value}s"
                )
                time.sleep(remaining_sleep)

            total_elapsed = time.time() - start_time
            self.logger.info(
                f"Action sequence completed in {total_elapsed:.2f}s (planned: {time_value}s)"
            )

            # Check if all actions succeeded - but don't fail the entire sequence if some robots failed
            success_count = sum(results) if results else 0
            total_count = len(results) if results else 0

            if total_count > 0:
                self.logger.info(
                    f"Action execution results: {success_count}/{total_count} robots succeeded"
                )
                return success_count > 0  # Return true if at least one robot succeeded
            else:
                self.logger.warning("No robot actions were executed")
                return True  # Don't fail if no actions were attempted

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
