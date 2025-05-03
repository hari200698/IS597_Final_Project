
import uuid

class Sensor:
    """
    Base class for vehicle sensors.

    Attributes:
        name (str): Sensor name
        type (str): Sensor type (camera, lidar, radar, etc.)
        position (Position3D): Sensor's position and orientation
        range (float): Maximum detection range in meters
        id (str): Unique identifier for the sensor
    """
    def __init__(self, name: str, type: str, position: Position3D, range: float):
        self.name = name
        self.type = type
        self.position = position
        self.range = range
        self.id = str(uuid.uuid4())  # Assign a unique ID

    def __str__(self) -> str:
        return f"{self.type.capitalize()} '{self.name}' at {self.position}"

    def can_detect(self, target_position: Position3D) -> bool:
        """
        Check if a target is within detection range.

        Args:
            target_position: Position of target to detect

        Returns:
            bool: True if target is within range
        """
        distance = self.position.distance_to(target_position)
        return distance <= self.range
