from typing import Dict, List, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
import uuid
from ..core.position import Position3D
from ..sensors.base import Sensor
from ..sensors.camera import Camera
from ..sensors.lidar import Lidar
from ..sensors.radar import Radar


class VehicleSensorSystem:
    """
    Manages all sensors on a vehicle.

    Attributes:
        sensors (Dict[str, Sensor]): Dictionary of sensors by name
    """
    def __init__(self):
        self.sensors = {}

    def add_sensor(self, sensor: Sensor):
        """Add a sensor to the system."""
        self.sensors[sensor.name] = sensor

    def remove_sensor(self, sensor_name: str):
        """Remove a sensor from the system."""
        if sensor_name in self.sensors:
            del self.sensors[sensor_name]

    def get_sensor(self, sensor_name: str) -> Optional[Sensor]:
        """Get a sensor by name."""
        return self.sensors.get(sensor_name)

    def detect_target(self, target_position: Position3D) -> Dict[str, bool]:
        """
        Check which sensors can detect a target.

        Args:
            target_position: Position of target to detect

        Returns:
            dict: Dictionary mapping sensor names to detection status
        """
        results = {}
        for name, sensor in self.sensors.items():
            results[name] = sensor.can_detect(target_position)
        return results

    def get_detecting_sensors(self, target_position: Position3D) -> List[Sensor]:
        """
        Get list of sensors that can detect a target.

        Args:
            target_position: Position of target to detect

        Returns:
            list: List of sensors that can detect the target
        """
        return [
            sensor for sensor in self.sensors.values()
            if sensor.can_detect(target_position)
        ]

    def get_sensor_coverage_stats(self) -> Dict[str, Any]:
        """
        Calculate statistics about sensor coverage.

        Returns:
            dict: Statistics about sensor coverage
        """
        stats = {
            "total_sensors": len(self.sensors),
            "by_type": {},
            "max_range": 0,
            "sensor_positions": {}
        }

        # Count sensors by type
        for sensor in self.sensors.values():
            sensor_type = sensor.type
            if sensor_type not in stats["by_type"]:
                stats["by_type"][sensor_type] = 0
            stats["by_type"][sensor_type] += 1

            # Track maximum range
            stats["max_range"] = max(stats["max_range"], sensor.range)

            # Record positions
            stats["sensor_positions"][sensor.name] = sensor.position.to_dict()

        return stats

    def from_configuration(self, config: Dict[str, Dict[str, Any]]):
        """
        Build sensor system from a configuration dictionary.

        Args:
            config: Dictionary mapping sensor names to their configurations
        """
        for name, sensor_config in config.items():
            sensor_type = sensor_config["type"]

            # Create Position3D from config
            pos_data = sensor_config["position"]
            orientation = sensor_config["orientation"]
            position = Position3D(
                x=pos_data[0],
                y=pos_data[1],
                z=pos_data[2],
                roll=orientation[0],  # Now properly using roll
                pitch=orientation[1],
                yaw=orientation[2]
            )

            # Create appropriate sensor type
            if sensor_type == "camera":
                sensor = Camera(
                    name=name,
                    position=position,
                    range=sensor_config["range"],
                    resolution=tuple(sensor_config["resolution"]),
                    fov=sensor_config["field_of_view"]
                )
            elif sensor_type == "lidar":
                sensor = Lidar(
                    name=name,
                    position=position,
                    range=sensor_config["range"],
                    horizontal_fov=sensor_config["horizontal_fov"],
                    vertical_fov=sensor_config["vertical_fov"],
                    points_per_second=sensor_config["points_per_second"]
                )
            elif sensor_type == "radar":
                sensor = Radar(
                    name=name,
                    position=position,
                    range=sensor_config["range"],
                    fov=sensor_config["field_of_view"],
                    resolution=sensor_config["resolution"]
                )
            else:
                raise ValueError(f"Unknown sensor type: {sensor_type}")

            self.add_sensor(sensor)
