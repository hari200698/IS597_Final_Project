import math
from typing import Dict, List, Tuple, Any, Optional

class Position3D:
    """
    Represents a 3D position and orientation in space.

    Attributes:
        x (float): X coordinate (forward/backward)
        y (float): Y coordinate (left/right)
        z (float): Z coordinate (up/down)
        roll (float): Roll angle in degrees (rotation around X-axis)
        pitch (float): Pitch angle in degrees (rotation around Y-axis)
        yaw (float): Yaw angle in degrees (rotation around Z-axis)
    """
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0,
                 roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll  # in degrees
        self.pitch = pitch  # in degrees
        self.yaw = yaw      # in degrees

    def __str__(self) -> str:
        return f"Position3D(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f}, " \
               f"roll={self.roll:.2f}°, pitch={self.pitch:.2f}°, yaw={self.yaw:.2f}°)"

    def to_dict(self) -> Dict[str, float]:
        """Convert position to dictionary format."""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'roll': self.roll,
            'pitch': self.pitch,
            'yaw': self.yaw
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Position3D':
        """Create Position3D object from dictionary."""
        return cls(
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            z=data.get('z', 0.0),
            roll=data.get('roll', 0.0),
            pitch=data.get('pitch', 0.0),
            yaw=data.get('yaw', 0.0)
        )

    def distance_to(self, other: 'Position3D') -> float:
        """ Calculate Euclidean distance to another Position3D."""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )

    def direction_to(self, other: 'Position3D') -> Tuple[float, float, float]:
        """
        Calculate direction (roll, pitch, yaw) from this position to another,
        taking into account the current orientation.

        Returns:
            tuple: (roll, pitch, yaw) in degrees
        """
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z

        # Calculate horizontal distance
        horizontal_distance = math.sqrt(dx**2 + dy**2)

        # Calculate pitch (elevation angle)
        target_pitch = math.degrees(math.atan2(dz, horizontal_distance))

        # Calculate yaw (azimuth angle)
        target_yaw = math.degrees(math.atan2(dy, dx))

        # Calculate roll - in this simple scenario, using the same roll as the current position
        target_roll = self.roll

        # Relative pitch (considering current pitch orientation)
        relative_pitch = target_pitch - self.pitch

        # Adjusting yaw for current orientation - normalizing to -180 to +180 range
        relative_yaw = target_yaw - self.yaw
        if relative_yaw > 180:
            relative_yaw -= 360
        elif relative_yaw < -180:
            relative_yaw += 360

        # Calculate relative roll
        relative_roll = target_roll - self.roll
        # Normalize to -180 to +180 range
        if relative_roll > 180:
          relative_roll -= 360
        elif relative_roll < -180:
          relative_roll += 360

        return relative_roll, relative_pitch, relative_yaw

    def is_within_field_of_view(self, target: 'Position3D',
                               horizontal_fov: float, vertical_fov: float) -> bool:
        """
        Check if target position is within field of view from this position.

        Args:
            target: Target position to check
            horizontal_fov: Horizontal field of view in degrees
            vertical_fov: Vertical field of view in degrees

        Returns:
            bool: True if target is within field of view
        """
        _, rel_pitch, rel_yaw = self.direction_to(target)

        return (abs(rel_yaw)   <= horizontal_fov / 2 and
                abs(rel_pitch) <= vertical_fov   / 2)
