"""
Configuration management for the robot action planner.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RobotConfig:
    """Configuration for generic robots."""

    ips: List[str]
    enabled: bool = True


@dataclass
class DroneConfig:
    """Configuration for drones."""

    simulator_mode: bool
    simulator_ip: str
    real_hosts: List[str]
    simulator_ports: Dict[str, Dict[str, int]]
    enabled: bool = True


@dataclass
class DogConfig:
    """Configuration for dog robots."""

    ips: List[str]
    ports: List[int]
    enabled: bool = True


@dataclass
class SpreadsheetConfig:
    """Configuration for Google Spreadsheets."""

    action_sequence_id: str
    action_details_id: str


@dataclass
class SimulatorConfig:
    """Configuration for simulator integration."""

    base_url: Optional[str]
    session_key: str
    song_base_url: str


@dataclass
class AppConfig:
    """Main application configuration."""

    robots: RobotConfig
    drones: DroneConfig
    dogs: DogConfig
    spreadsheet: SpreadsheetConfig
    simulator: SimulatorConfig

    @classmethod
    def from_constants(cls) -> "AppConfig":
        """Create configuration from existing constants file."""
        # Import here to avoid circular imports
        import constant

        return cls(
            robots=RobotConfig(ips=constant.ROBOT_IPS, enabled=True),
            drones=DroneConfig(
                simulator_mode=constant.DRONE_SIMULATOR,
                simulator_ip=constant.DRONE_SIMULATOR_IP,
                real_hosts=constant.DRONE_REAL_HOSTS,
                simulator_ports=constant.DRONE_SIMULATOR_PORTS,
                enabled=not constant.SKIP_DRONES,
            ),
            dogs=DogConfig(
                ips=constant.DOG_IPS,
                ports=constant.DOG_PORTS,
                enabled=not constant.SKIP_DOGS,
            ),
            spreadsheet=SpreadsheetConfig(
                action_sequence_id=constant.ACTION_SEQUENCE_SPREADSHEET_ID,
                action_details_id=constant.ACTION_DETAILS_SPREADSHEET_ID,
            ),
            simulator=SimulatorConfig(
                base_url=constant.SIMULATOR_BASE_URL,
                session_key=constant.SESSION_KEY,
                song_base_url=constant.SONG_BASE_URL,
            ),
        )
