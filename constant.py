# Constants for robot-group-action-planner

# Google Spreadsheet IDs
ACTION_SEQUENCE_SPREADSHEET_ID = "1JmjO4Yidu2pLtJxEuu4mYPX14AYmEj0przne75JBg6Y"
ACTION_DETAILS_SPREADSHEET_ID = "1Bsgc60s3m_-dxhneTedxFlCCYxEp-9Ippu3Yr8dekxo"

# Robot IP addresses
ROBOT_IPS = [
    "http://192.168.137.7:9030",
    "http://192.168.137.2:9030",
    "http://192.168.137.3:9030",
    "http://192.168.137.4:9030",
    "http://192.168.137.5:9030",
    "http://192.168.137.6:9030",
]

# Dog robot configuration
DOG_IPS = ["192.168.137.41", "192.168.137.42"]  # IP addresses for 2 dog robots
DOG_PORTS = [8830, 8830]  # UDP ports for dog robots (typically same port)

# Drone configuration
DRONE_SIMULATOR = False
DRONE_SIMULATOR_IP = "192.168.25.128"
DRONE_REAL_HOSTS = ["192.168.137.31", "192.168.137.32"]
DRONE_SIMULATOR_PORTS = {
    "drone1": {"control_udp": 8889, "state_udp": 8890},
    "drone2": {"control_udp": 8890, "state_udp": 8891},
}

SIMULATOR_BASE_URL = "https://iyfjqmah49.us-east-1.awsapprunner.com"
SESSION_KEY = "hkiitshow"
SONG_BASE_URL = "https://cdkstack-robotsimulatorconstructrobotsimulatorwebs-fxuvfxmglhc4.s3.us-east-1.amazonaws.com"

ENABLE_DRONES = True  # Set to False to disable drone initialization
ENABLE_DOGS = True  # Set to False to disable dog initialization
ENABLE_ROBOTS = True  # Set to False to disable robot initialization
