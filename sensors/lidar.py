from ..core.position import Position3D
from .base import Sensor

class Lidar(Sensor):
    """
    Lidar sensor for 3D point cloud detection.

    Attributes:
        horizontal_fov (float): Horizontal field of view in degrees
        vertical_fov (float): Vertical field of view in degrees
    """
    def __init__(self, name: str, position: Position3D, range: float,
                 horizontal_fov: float, vertical_fov: float):
        super().__init__(name, "lidar", position, range)
        self.horizontal_fov = horizontal_fov
        self.vertical_fov = vertical_fov

    def can_detect(self, target_position: Position3D) -> bool:
        """
        Check if target is within lidar's field of view and range.

        Args:
            target_position: Position of target to detect

        Returns:
            bool: True if target is within range and FOV
        """
        if not super().can_detect(target_position):
            return False

        # Check if within field of view
        return self.position.is_within_field_of_view(
            target_position, self.horizontal_fov, self.vertical_fov
        )
