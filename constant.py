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

# Drone configuration
DRONE_SIMULATOR = True
DRONE_SIMULATOR_IP = "192.168.25.128"
DRONE_REAL_HOSTS = ["192.168.137.21", "192.168.137.22"]
DRONE_SIMULATOR_PORTS = {
    "drone1": {"control_udp": 8889, "state_udp": 8890},
    "drone2": {"control_udp": 8890, "state_udp": 8891},
}

SIMULATOR_BASE_URL = "https://iyfjqmah49.us-east-1.awsapprunner.com"
SESSION_KEY = "cywong@vtc.edu.hk"
SONG_BASE_URL = "https://cdkstack-robotsimulatorconstructrobotsimulatorwebs-fxuvfxmglhc4.s3.us-east-1.amazonaws.com"
SKIP_DRONES = True  # Set to True to skip drone initialization
