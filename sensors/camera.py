from typing import Tuple
from ..core.position import Position3D
from .base import Sensor

class Camera(Sensor):
    """
    Camera sensor for visual detection.

    Attributes:
        resolution (Tuple[int, int]): Camera resolution (width, height)
        fov (float): Horizontal field of view in degrees
    """
    def __init__(self, name: str, position: Position3D, range: float,
                 resolution: Tuple[int, int], fov: float):
        super().__init__(name, "camera", position, range)
        self.resolution = resolution
        self.fov = fov
        self.vertical_fov = fov * (resolution[1] / resolution[0])  # Approximation based on aspect ratio

    def can_detect(self, target_position: Position3D) -> bool:
        """
        Check if target is within camera's field of view and range.

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
