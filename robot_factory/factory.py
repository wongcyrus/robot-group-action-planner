"""
Robot factory for creating robot instances.
"""

import logging
from typing import Any, Dict, List

from robot_types.dog_action import DogAction
from robot_types.drone_action import DroneAction
from robot_types.humanoid_action import HumanoidAction


class RobotFactory:
    """Factory for creating robot instances."""

    def __init__(self, config):
        """Initialize robot factory."""
        self.config = config
        self.logger = logging.getLogger("RobotFactory")

    def create_all_robots(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int],
    ) -> Dict[str, List[Any]]:
        """Create all configured robots."""
        robots = {}

        try:
            # Create HTTP humanoids
            if self.config.robots.enabled:
                robots["robots"] = self._create_http_humanoids(
                    action_name_to_time, action_name_to_repeat_time
                )

            # Create drones
            if self.config.drones.enabled:
                robots["drones"] = self._create_drones(
                    action_name_to_time, action_name_to_repeat_time
                )

            # Create dogs
            if self.config.dogs.enabled:
                robots["dogs"] = self._create_dogs(
                    action_name_to_time, action_name_to_repeat_time
                )

            return robots

        except Exception as e:
            self.logger.error(f"Error creating robots: {e}")
            return {}

    def _create_http_humanoids(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int],
    ) -> List[HumanoidAction]:
        """Create HTTP humanoids."""
        robots = []

        try:
            for i, ip in enumerate(self.config.robots.ips):
                robot_id = f"humanoid_{i+1}"
                api_url = f"http://{ip}:{self.config.robots.port}"

                robot = HumanoidAction(
                    api_url=api_url,
                    action_name_to_time=action_name_to_time,
                    action_name_to_repeat_time=action_name_to_repeat_time,
                    robot_id=robot_id,
                )
                robots.append(robot)
                self.logger.info(f"Created HTTP humanoid: {robot_id} at {api_url}")

        except Exception as e:
            self.logger.error(f"Error creating HTTP humanoids: {e}")

        return robots

    def _create_drones(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int],
    ) -> List[DroneAction]:
        """Create drone instances."""
        drones = []

        try:
            # Create real drones if hosts are specified
            if self.config.drones.real_hosts:
                for i, host in enumerate(self.config.drones.real_hosts):
                    drone_id = f"drone_{i+1}"

                    drone = DroneAction(
                        action_name_to_time=action_name_to_time,
                        action_name_to_repeat_time=action_name_to_repeat_time,
                        drone_id=drone_id,
                        host=host,
                        control_udp=8889,  # Default Tello control port
                        state_udp=8890,  # Default Tello state port
                    )
                    drones.append(drone)
                    self.logger.info(f"Created real drone: {drone_id} at {host}")

            # Create simulator drones if enabled
            elif self.config.drones.simulator_mode:
                for drone_name, ports in self.config.drones.simulator_ports.items():
                    drone_id = f"sim_{drone_name}"

                    drone = DroneAction(
                        action_name_to_time=action_name_to_time,
                        action_name_to_repeat_time=action_name_to_repeat_time,
                        drone_id=drone_id,
                        host=self.config.drones.simulator_ip,
                        control_udp=ports["control_udp"],
                        state_udp=ports["state_udp"],
                    )
                    drones.append(drone)
                    self.logger.info(
                        f"Created simulator drone: {drone_id} at {self.config.drones.simulator_ip}:{ports['control_udp']}"
                    )

        except Exception as e:
            self.logger.error(f"Error creating drones: {e}")

        return drones

    def _create_dogs(
        self,
        action_name_to_time: Dict[str, float],
        action_name_to_repeat_time: Dict[str, int],
    ) -> List[DogAction]:
        """Create dog robot instances."""
        dogs = []

        try:
            for i, ip in enumerate(self.config.dogs.ips):
                dog_id = f"dog_{i+1}"
                # Get port for this dog (use index if available, otherwise first port)
                port = (
                    self.config.dogs.ports[i]
                    if i < len(self.config.dogs.ports)
                    else self.config.dogs.ports[0]
                )

                dog = DogAction(
                    action_name_to_time=action_name_to_time,
                    action_name_to_repeat_time=action_name_to_repeat_time,
                    dog_id=dog_id,
                    robot_ip=ip,
                    robot_port=port,
                )
                dogs.append(dog)
                self.logger.info(f"Created dog robot: {dog_id} at {ip}:{port}")

        except Exception as e:
            self.logger.error(f"Error creating dogs: {e}")

        return dogs
