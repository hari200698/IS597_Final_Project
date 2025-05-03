import random
import uuid
import numpy as np
from typing import List, Dict, Any

def create_object_detection_simulation(num_objects=50, area_size=150, seed=42):
    """Create a simulation with randomly placed objects in a defined area.

    Args:
        num_objects: Number of objects to place in the simulation
        area_size: Size of the square area in meters
        seed: Random seed for reproducibility

    Returns:
        List of objects with their positions and types
    """
    # Set seeds for reproducibility
    random.seed(seed)
    np.random.seed(seed)

    objects = []
    object_types = ['pedestrian', 'vehicle', 'cyclist', 'static_obstacle']
    object_type_weights = [0.1, 0.6, 0.2, 0.1]  # Probability distribution for object types

    half_area = area_size / 2.0

    for _ in range(num_objects):
        obj_type = random.choices(object_types, weights=object_type_weights, k=1)[0]
        x = random.uniform(-half_area, half_area)
        y = random.uniform(-half_area, half_area)

        # Add some randomness to object dimensions based on type
        if obj_type == 'pedestrian':
            width = random.uniform(0.4, 0.6)
            length = random.uniform(0.4, 0.6)
            height = random.uniform(1.5, 2.0)
        elif obj_type == 'vehicle':
            width = random.uniform(1.8, 2.5)
            length = random.uniform(4.0, 6.0)
            height = random.uniform(1.4, 2.0)
        elif obj_type == 'cyclist':
            width = random.uniform(0.5, 0.8)
            length = random.uniform(1.7, 2.0)
            height = random.uniform(1.5, 2.0)
        else:  # static_obstacle
            width = random.uniform(0.5, 3.0)
            length = random.uniform(0.5, 3.0)
            height = random.uniform(0.5, 3.0)

        objects.append({
            'type': obj_type,
            'position': (x, y),
            'width': width,
            'length': length,
            'height': height,
            'id': str(uuid.uuid4())  # Add unique ID for tracking
        })

    return objects
