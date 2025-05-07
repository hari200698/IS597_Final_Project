from ..core.position import Position3D
from .base import Sensor

class Radar(Sensor):
    """
    Radar sensor for velocity and distance detection.

    Attributes:
        fov (float): Field of view in degrees
        resolution (str): Resolution quality (low, medium, high)
    """
    def __init__(self, name: str, position: Position3D, range: float,
                 fov: float):
        super().__init__(name, "radar", position, range)
        self.fov = fov
        # For simplicity, assuming vertical FOV is 1/3 of horizontal
        self.vertical_fov = self.fov / 3

    def can_detect(self, target_position: Position3D) -> bool:
        """
        Check if target is within radar's field of view and range.

        Args:
            target_position: Position of target to detect

        Returns:
            bool: True if target is within range and FOV
        """
        if not super().can_detect(target_position):
            return False

        # Check if within field of view
        return self.position.is_within_field_of_view(
            target_position, self.fov, self.vertical_fov
        )
