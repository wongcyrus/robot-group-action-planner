# Constants for robot-group-action-planner

# Google Spreadsheet IDs
ACTION_SEQUENCE_SPREADSHEET_ID = "1JmjO4Yidu2pLtJxEuu4mYPX14AYmEj0przne75JBg6Y"
ACTION_DETAILS_SPREADSHEET_ID = "1Bsgc60s3m_-dxhneTedxFlCCYxEp-9Ippu3Yr8dekxo"

# Humanoid robot IP addresses (formerly generic "robots")
HUMANOID_IPS = [
    "192.168.137.7",
    "192.168.137.2",
    "192.168.137.3",
    "192.168.137.4",
    "192.168.137.5",
    "192.168.137.6",
]

# Dog robot configuration
# DOG_IPS = ["192.168.137.42"]  # IP addresses for 1 dog robots

DOG_IPS = [ "192.168.137.42","192.168.137.41"]  # IP addresses for 2 dog robots
DOG_PORTS = [8830, 8830]  # UDP ports for dog robots (typically same port)

# Drone configuration
DRONE_SIMULATOR = False
DRONE_SIMULATOR_IP = "192.168.25.128"
# DRONE_REAL_HOSTS = ["192.168.137.22"]
DRONE_REAL_HOSTS = ["192.168.137.21", "192.168.137.22"]

DRONE_SIMULATOR_PORTS = {
    "drone1": {"control_udp": 8889, "state_udp": 8890},
    "drone2": {"control_udp": 8890, "state_udp": 8891},
}

SIMULATOR_BASE_URL = "https://iyfjqmah49.us-east-1.awsapprunner.com"
SESSION_KEY = "hkiitshow"
SONG_BASE_URL = "https://cdkstack-robotsimulatorconstructrobotsimulatorwebs-fxuvfxmglhc4.s3.us-east-1.amazonaws.com"

ENABLE_DRONES = True  # Set to False to disable drone initialization
ENABLE_DOGS = True  # Set to False to disable dog initialization
ENABLE_HUMANOIDS = True  # Set to False to disable humanoid robot initialization

# Drone timeout configuration
DRONE_CONNECTION_TIMEOUT = 2  # Timeout for drone connection attempts (seconds)
DRONE_COMMAND_TIMEOUT = 2  # Timeout for individual drone commands (seconds)
DRONE_TAKEOFF_TIMEOUT = 8  # Timeout for takeoff commands (seconds)

# Cache configuration
USE_FILE_CACHE = False  # Set to False to disable persistent file caching
CACHE_DIRECTORY = "cache"  # Directory to store cache files
CACHE_EXPIRY_HOURS = 24  # Cache expiry time in hours (0 = never expire)

# Log configuration
RESET_LOGS = True  # Set to True to delete all log files when program starts

# Default action timings for different robot types
# These values are extracted from the action classes to centralize timing configuration

# Dog robot default action timings (seconds)
DOG_DEFAULT_ACTION_TIMES = {
    # Basic movement actions
    "forward": 3.0,
    "back": 3.0,
    "left": 3.0,
    "right": 3.0,
    # Posture actions
    "sit": 2.0,
    "stand": 2.0,
    "lay_down": 2.0,
    # Mode changes
    "activate": 1.0,
    "walk_mode": 1.0,
    "dance_mode": 1.0,
    # Stop action
    "stop": 1.0,
}

# Drone robot default action timings (seconds)
DRONE_DEFAULT_ACTION_TIMES = {
    # Takeoff and landing
    "takeoff": 3.0,
    "land": 3.0,
    # Movement actions (with common parameter variations)
    "move_up": 3.0,
    "move_up_20": 3.0,
    "move_up_50": 3.0,
    "move_up_100": 3.0,
    "move_down": 3.0,
    "move_down_20": 3.0,
    "move_down_50": 3.0,
    "move_down_100": 3.0,
    "move_left": 3.0,
    "move_left_20": 3.0,
    "move_left_50": 3.0,
    "move_left_100": 3.0,
    "move_right": 3.0,
    "move_right_20": 3.0,
    "move_right_50": 3.0,
    "move_right_100": 3.0,
    "move_forward": 3.0,
    "move_forward_20": 3.0,
    "move_forward_50": 3.0,
    "move_forward_100": 3.0,
    "move_back": 3.0,
    "move_back_20": 3.0,
    "move_back_50": 3.0,
    "move_back_100": 3.0,
    # Rotation actions
    "rotate_cw": 3.0,
    "rotate_cw_90": 3.0,
    "rotate_cw_180": 3.0,
    "rotate_ccw": 3.0,
    "rotate_ccw_90": 3.0,
    "rotate_ccw_180": 3.0,
    # Flip actions
    "flip_forward": 4.0,
    "flip_back": 4.0,
    "flip_left": 4.0,
    "flip_right": 4.0,
    # Special actions
    "hover": 4.0,
    # Complex movement actions
    "curve": 7.0,
    "go": 3.0,
    "jump": 5.0,
}

# Drone action pattern fallback timings (for actions that match patterns but aren't in the main dict)
DRONE_PATTERN_FALLBACK_TIMES = {
    "takeoff": 3.0,
    "land": 3.0,
    "hover": 4.0,
    "curve": 7.0,  # Complex curve movements
    "go": 3.0,  # XYZ movement actions
    "jump": 5.0,  # Jump actions
    "move": 3.0,  # Base movement pattern
    "rotate": 3.0,  # Base rotation pattern
    "flip": 4.0,  # Base flip pattern
}

# Dog action pattern fallback timings (for actions that match patterns but aren't in the main dict)
DOG_PATTERN_FALLBACK_TIMES = {
    "forward": 3.0,
    "back": 3.0,
    "left": 3.0,
    "right": 3.0,
    "sit": 2.0,
    "stand": 2.0,
    "lay_down": 2.0,
    "activate": 1.0,
    "walk_mode": 1.0,
    "dance_mode": 1.0,
    "stop": 1.0,
}
