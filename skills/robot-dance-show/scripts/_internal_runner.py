import os
import sys
import argparse
import logging

# Ensure the project root is in the path so we can import core modules
# This script is internal to the robot-dance-show skill.
# It resolves the project root relative to its position within the skill folder.
# skills/robot-dance-show/scripts/dance_runner.py -> project_root is 3 levels up
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(project_root)

# GUARDRAIL: Prevent accidental direct execution
if os.environ.get("ROBOT_DANCE_AUTHORIZED") != "true":
    print("CRITICAL ERROR: Direct execution of the internal runner is forbidden.")
    print("You MUST use the environment-aware launcher instead:")
    print("  ./skills/robot-dance-show/scripts/launcher.sh \"<SONG_NAME>\"")
    sys.exit(1)

try:
    from config.settings import AppConfig
    from core.action_compiler import ActionCompiler
    from core.spreadsheet_loader import SpreadsheetLoader
    from tools import setup_logging
except ImportError as e:
    print(f"Error: Could not import core modules from project root. {e}")
    sys.exit(1)

def execute_dance_show(song_name: str):
    """
    Skill-internal orchestrator for robot dance shows.
    Encapsulates the specific logic required for synchronized robot performances.
    """
    setup_logging()
    logger = logging.getLogger("RobotDanceShow")
    logger.info(f"Initiating robot dance show for: {song_name}")

    # Specific dance-show orchestration logic goes here.
    # This script owns the execution lifecycle for this specific skill.
    print(f"Executing robot dance choreography for {song_name}...")
    
    # Logic to interface with robot_factory and execution_engine
    # ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot Dance Show Internal Runner")
    parser.add_argument("song", help="The name of the song to perform")
    args = parser.parse_args()
    
    execute_dance_show(args.song)
