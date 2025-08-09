"""
Robot Action Planner - Main Entry Point
Refactored version with improved architecture and error handling.
"""

import logging
import os
import sys
import threading
import time

# Import modules
from config.settings import AppConfig
from core.action_compiler import ActionCompiler
from core.cache_manager import cache_manager
from core.spreadsheet_loader import SpreadsheetLoader
from tools import reset_logs, setup_logging


class RobotActionPlanner:
    """Main orchestrator for robot action planning and execution."""

    def __init__(self, config: AppConfig):
        """
        Initialize the robot action planner.

        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger("RobotActionPlanner")
        self.stop_event = threading.Event()

        # Initialize components
        from playback.engine import ExecutionEngine
        from playback.manager import MediaManager
        from robot_factory.factory import RobotFactory

        self.robot_factory = RobotFactory(config)
        self.execution_engine = ExecutionEngine()
        self.media_manager = MediaManager(config)

        # Statistics tracking
        self.stats = {
            "songs_processed": 0,
            "songs_failed": 0,
            "total_actions_executed": 0,
            "robots_initialized": 0,
        }

        # Cache for pre-loaded data
        self.cached_song_data = {}
        self.cached_action_mappings = None

    def run(self) -> None:
        """Run the main application loop."""
        self.logger.info("Starting Robot Action Planner (Refactored)")

        try:
            # Validate configuration
            if not self._validate_configuration():
                self.logger.error("Configuration validation failed")
                return

            # Find song files
            song_folder = self._get_song_folder()
            song_files = self.media_manager.get_song_files(song_folder)

            if not song_files:
                self.logger.error(f"No .mp4 files found in {song_folder}")
                return

            self.logger.info(f"Found {len(song_files)} song files to process")

            # Pre-load all spreadsheet data for all songs
            self._preload_all_song_data(song_files)

            # Process each song
            for song_file in song_files:
                if self.stop_event.is_set():
                    self.logger.info("Stop event detected, exiting main loop")
                    break

                song_name = os.path.splitext(song_file)[0]
                song_file_path = os.path.join(song_folder, song_file)

                self.logger.info(f"Processing song: {song_name}")
                success = self._process_single_song(song_file_path, song_name)

                if success:
                    self.stats["songs_processed"] += 1
                    self.logger.info(f"Successfully processed song: {song_name}")
                else:
                    self.stats["songs_failed"] += 1
                    self.logger.error(f"Failed to process song: {song_name}")

                # Small delay between songs if not the last one
                if song_file != song_files[-1] and not self.stop_event.is_set():
                    self.logger.info("Waiting 3 seconds before next song...")
                    time.sleep(3)

        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user (Ctrl+C)")
            self.stop_event.set()
        except Exception as e:
            self.logger.error(
                f"Unexpected error in main application: {e}", exc_info=True
            )
        finally:
            self._cleanup()
            self._print_statistics()

    def _validate_configuration(self) -> bool:
        """Validate the application configuration."""
        try:
            # Check if at least one robot type is enabled
            enabled_types = []
            if self.config.robots.enabled and self.config.robots.ips:
                enabled_types.append("robots")
            if self.config.drones.enabled and (
                self.config.drones.real_hosts or self.config.drones.simulator_mode
            ):
                enabled_types.append("drones")
            if self.config.dogs.enabled and self.config.dogs.ips:
                enabled_types.append("dogs")

            if not enabled_types:
                self.logger.error("No robot types are enabled or configured")
                return False

            self.logger.info(f"Enabled robot types: {', '.join(enabled_types)}")

            # Validate spreadsheet configuration
            if not self.config.spreadsheet.action_sequence_id:
                self.logger.error("No action sequence spreadsheet ID configured")
                return False

            if not self.config.spreadsheet.action_details_id:
                self.logger.error("No action details spreadsheet ID configured")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return False

    def _get_song_folder(self) -> str:
        """Get the song folder path."""
        song_folder = os.path.join(os.path.dirname(__file__), "songs")
        return os.path.abspath(song_folder)

    def _preload_all_song_data(self, song_files: list) -> None:
        """
        Pre-load all spreadsheet data for all songs to cache it for faster access.

        Args:
            song_files: List of song file names to preload data for
        """
        self.logger.info("Pre-loading spreadsheet data for all songs...")
        start_time = time.time()

        # Clean up expired cache files
        cleanup_count = cache_manager.cleanup_expired_cache()
        if cleanup_count > 0:
            self.logger.info(f"Cleaned up {cleanup_count} expired cache files")

        # Extract song names from file names
        song_names = [os.path.splitext(song_file)[0] for song_file in song_files]

        # Load action details once (this is already cached in SpreadsheetLoader)
        self.logger.info("Loading action details...")
        temp_loader = SpreadsheetLoader(song_names[0] if song_names else "dummy")
        self.cached_action_mappings = {
            "action_name_to_time": temp_loader.get_action_name_to_time(),
            "action_name_to_repeat_time": temp_loader.get_action_name_to_repeat_time(),
        }

        # Load robot actions for each song
        for i, song_name in enumerate(song_names, 1):
            self.logger.info(
                f"Pre-loading data for song {i}/{len(song_names)}: {song_name}"
            )
            try:
                # Load spreadsheet data for this song
                spreadsheet_loader = SpreadsheetLoader(song_name)
                action_compiler = ActionCompiler(spreadsheet_loader)
                # Compile actions and automatically export to CSV cache
                robot_actions = action_compiler.compile_actions(
                    export_excel=True, song_name=song_name
                )

                # Cache the compiled data
                self.cached_song_data[song_name] = {
                    "robot_actions": robot_actions,
                    "spreadsheet_loader": spreadsheet_loader,  # Keep reference for other methods
                }

                self.logger.debug(
                    f"Cached {len(robot_actions)} action sequences for {song_name}"
                )

            except Exception as e:
                self.logger.error(f"Failed to preload data for song {song_name}: {e}")
                # Store empty data to prevent processing this song later
                self.cached_song_data[song_name] = {
                    "robot_actions": [],
                    "spreadsheet_loader": None,
                }

        load_time = time.time() - start_time
        successful_loads = sum(
            1 for data in self.cached_song_data.values() if data["robot_actions"]
        )
        self.logger.info(
            f"Pre-loading completed in {load_time:.2f}s. "
            f"Successfully loaded {successful_loads}/{len(song_names)} songs."
        )

        # Log cache information
        cache_info = cache_manager.get_cache_info()
        if cache_info["load_enabled"] or cache_info["save_enabled"]:
            cache_status = []
            if cache_info["load_enabled"]:
                cache_status.append("loading")
            if cache_info["save_enabled"]:
                cache_status.append("saving")
            
            self.logger.info(
                f"File cache ({'/'.join(cache_status)}): {cache_info['total_files']} files, "
                f"{cache_info['total_size_bytes']} bytes"
            )
        else:
            self.logger.info("File cache is disabled")

    def _process_single_song(self, song_file_path: str, song_name: str) -> bool:
        """
        Process a single song: get cached actions, initialize robots, and execute.

        Args:
            song_file_path: Full path to the song file
            song_name: Song name without extension

        Returns:
            True if processing was successful, False otherwise
        """
        robots = {}
        try:
            # Get cached data
            self.logger.info(f"Using cached spreadsheet data for song: {song_name}")

            if song_name not in self.cached_song_data:
                self.logger.error(f"No cached data found for song: {song_name}")
                return False

            cached_data = self.cached_song_data[song_name]
            robot_actions = cached_data["robot_actions"]

            if not robot_actions:
                self.logger.warning(f"No robot actions found for song: {song_name}")
                return False

            # Use cached action mappings
            action_name_to_time = self.cached_action_mappings["action_name_to_time"]
            action_name_to_repeat_time = self.cached_action_mappings[
                "action_name_to_repeat_time"
            ]

            self.logger.info(f"Loaded {len(robot_actions)} action sequences (cached)")
            self.logger.info(
                f"Loaded {len(action_name_to_time)} action definitions (cached)"
            )

            # Initialize robots
            self.logger.info("Initializing robots...")
            robots = self.robot_factory.create_all_robots(
                action_name_to_time, action_name_to_repeat_time
            )

            if not robots:
                self.logger.error("No robots were initialized successfully")
                return False

            # Count total robots
            total_robots = sum(len(robot_list) for robot_list in robots.values())
            self.stats["robots_initialized"] = total_robots
            self.logger.info(f"Successfully initialized {total_robots} robots")

            # Start media playback BEFORE action sequence loop (like original)
            self.logger.info(f"Starting media for song: {song_name}")

            if self.config.media.play_song_in_pc:
                media_success = self.media_manager.start_media_for_song(
                    song_file_path, song_name
                )
                if not media_success:
                    self.logger.warning(
                        f"Failed to start media for {song_name}, continuing anyway"
                    )
            else:
                self.media_manager.play_song_in_simulator(song_name)

            # Add delay to allow song to load properly
            self.logger.info("Waiting 1 seconds for song to load...")
            time.sleep(1)

            # Execute actions (the song will continue playing through all sequences)
            self.logger.info(f"Executing {len(robot_actions)} action sequences...")
            execution_success = self.execution_engine.execute_action_sequence(
                robots, robot_actions, self.stop_event
            )

            self.stats["total_actions_executed"] += len(robot_actions)

            # Stop media AFTER all action sequences complete (like original)
            if self.config.media.play_song_in_pc:
                self.media_manager.stop_media()

            return execution_success

        except Exception as e:
            self.logger.error(f"Error processing song {song_name}: {e}", exc_info=True)
            return False
        finally:
            # Always cleanup robots
            if robots:
                self.logger.info("Cleaning up robots...")
                self.execution_engine.cleanup_all_robots(robots)

    def _cleanup(self) -> None:
        """Perform application cleanup."""
        self.logger.info("Performing application cleanup")
        try:
            # Stop any remaining media
            self.media_manager.stop_media()

            # Set stop event to ensure all threads stop
            self.stop_event.set()

            # Give threads a moment to cleanup
            time.sleep(0.5)

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _print_statistics(self) -> None:
        """Print execution statistics."""
        self.logger.info("=" * 50)
        self.logger.info("EXECUTION STATISTICS")
        self.logger.info("=" * 50)
        self.logger.info(
            f"Songs processed successfully: {self.stats['songs_processed']}"
        )
        self.logger.info(f"Songs failed: {self.stats['songs_failed']}")
        self.logger.info(
            f"Total action sequences executed: {self.stats['total_actions_executed']}"
        )
        self.logger.info(f"Robots initialized: {self.stats['robots_initialized']}")

        # Add caching statistics
        total_cached = len(self.cached_song_data)
        successful_cached = sum(
            1 for data in self.cached_song_data.values() if data["robot_actions"]
        )
        self.logger.info(f"Songs cached: {successful_cached}/{total_cached}")

        # Add file cache statistics
        cache_info = cache_manager.get_cache_info()
        if cache_info["load_enabled"] or cache_info["save_enabled"]:
            cache_status = []
            if cache_info["load_enabled"]:
                cache_status.append("loading")
            if cache_info["save_enabled"]:
                cache_status.append("saving")
            
            self.logger.info(
                f"File cache ({'/'.join(cache_status)}): {cache_info['total_files']} files, "
                f"{cache_info['total_size_bytes']} bytes"
            )
        else:
            self.logger.info("File cache: Disabled")

        total_songs = self.stats["songs_processed"] + self.stats["songs_failed"]
        if total_songs > 0:
            success_rate = (self.stats["songs_processed"] / total_songs) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")

        self.logger.info("=" * 50)

    def shutdown(self) -> None:
        """Gracefully shutdown the application."""
        self.logger.info("Shutting down robot action planner")
        self.stop_event.set()


def main() -> None:
    """Main entry point for the application."""
    try:
        # Reset logs if enabled (before setting up logging)
        reset_logs()

        # Setup logging
        setup_logging()

        logger = logging.getLogger("Main")
        logger.info("Starting Robot Action Planner (Refactored)")
        logger.info(f"Working directory: {os.getcwd()}")

        # Load configuration
        logger.info("Loading configuration...")
        config = AppConfig.from_constants()

        # Create and run the application
        planner = RobotActionPlanner(config)
        planner.run()

        logger.info("Robot Action Planner completed successfully")

    except Exception as e:
        logger = logging.getLogger("Main")
        logger.error(f"Fatal error in main application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
