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

DOG_IPS = ["192.168.137.42", "192.168.137.41"]  # IP addresses for 2 dog robots
# Port 8081 is now fixed in the DogAction class - no need for DOG_PORTS array

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

ENABLE_DRONES = False  # Set to False to disable drone initialization
ENABLE_DOGS = False  # Set to False to disable dog initialization
ENABLE_HUMANOIDS = True  # Set to False to disable humanoid robot initialization

# Media playback configuration
PLAY_SONG_IN_PC = False  # Set to True to play song in PC, False to use simulator

# Drone timeout configuration
DRONE_CONNECTION_TIMEOUT = 2  # Timeout for drone connection attempts (seconds)
DRONE_COMMAND_TIMEOUT = 2  # Timeout for individual drone commands (seconds)
DRONE_TAKEOFF_TIMEOUT = 8  # Timeout for takeoff commands (seconds)

# Dog timeout and retry configuration
DOG_COMMAND_TIMEOUT = 3  # Timeout for individual dog commands (seconds)
DOG_MAX_RETRIES = 0  # Maximum number of retries for dog commands (0 = no retries)

# Cache configuration
USE_FILE_CACHE = False  # Set to False to disable loading from persistent file cache
ALWAYS_SAVE_CACHE = True  # Set to True to always save cache files for debugging (even when USE_FILE_CACHE is False)
CACHE_DIRECTORY = "data"  # Directory to store cache files
CACHE_EXPIRY_HOURS = 24  # Cache expiry time in hours (0 = never expire)

# Log configuration
RESET_LOGS = True  # Set to True to delete all log files when program starts
