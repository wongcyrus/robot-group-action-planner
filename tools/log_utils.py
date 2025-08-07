"""
Log utilities for robot-group-action-planner.
Contains functions for setting up logging and managing log files.
"""

import logging
import os
import glob
import constant


def reset_logs() -> None:
    """
    Delete all log files if RESET_LOGS is enabled.
    
    This function removes all log files from both 'logs' and 'log' directories
    when the RESET_LOGS constant is set to True.
    """
    if not constant.RESET_LOGS:
        return
    
    # Define log directories to clean
    log_directories = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
    ]
    
    files_deleted = 0
    
    for log_dir in log_directories:
        if os.path.exists(log_dir):
            # Find all log files (*.log and *.csv files)
            log_patterns = [
                os.path.join(log_dir, "*.log"),
                os.path.join(log_dir, "*.csv")
            ]
            
            for pattern in log_patterns:
                for log_file in glob.glob(pattern):
                    try:
                        os.remove(log_file)
                        files_deleted += 1
                        print(f"Deleted log file: {log_file}")
                    except OSError as e:
                        print(f"Warning: Could not delete log file {log_file}: {e}")
    
    if files_deleted > 0:
        print(f"Reset logs: Deleted {files_deleted} log file(s)")
    else:
        print("Reset logs: No log files found to delete")


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup application logging with centralized and individual robot type logs.
    
    Creates the following log files in the 'logs' directory:
    - robot_planner.log: Centralized log containing all application messages
    - humanoid_debug.log: Debug log for humanoid robot actions only
    - drone_debug.log: Debug log for drone robot actions only  
    - dog_debug.log: Debug log for dog robot actions only
    
    All logs use the same format and log level, but individual robot logs
    are filtered to contain only messages from their respective robot types.
    
    Args:
        log_level: Console logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Centralized file handler - logs everything
    log_file = os.path.join(log_dir, "robot_planner.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(logging.Formatter(log_format))

    # Root logger - receives all logs and sends them to centralized file and console
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Create individual debug log files for each robot type
    robot_types = {
        "humanoid": "humanoid_debug.log",
        "drone": "drone_debug.log", 
        "dog": "dog_debug.log"
    }

    for robot_type, log_filename in robot_types.items():
        # Create file handler for this robot type
        robot_log_file = os.path.join(log_dir, log_filename)
        robot_file_handler = logging.FileHandler(robot_log_file)
        robot_file_handler.setLevel(logging.DEBUG)
        robot_file_handler.setFormatter(logging.Formatter(log_format))

        # Create a filter to only log messages from this robot type
        class RobotTypeFilter:
            def __init__(self, robot_type):
                self.robot_type = robot_type.lower()
            
            def filter(self, record):
                # Check if the logger name contains the robot type
                logger_name = record.name.lower()
                return (self.robot_type in logger_name or 
                       f"{self.robot_type}action" in logger_name)

        robot_file_handler.addFilter(RobotTypeFilter(robot_type))
        
        # Add the handler to the root logger so it receives all messages
        root_logger.addHandler(robot_file_handler)

    # Log information about the logging setup
    setup_logger = logging.getLogger("LoggingSetup")
    setup_logger.info(f"Logging configured with centralized log: {log_file}")
    for robot_type, log_filename in robot_types.items():
        robot_log_path = os.path.join(log_dir, log_filename)
        setup_logger.info(f"Individual {robot_type} debug log: {robot_log_path}")
