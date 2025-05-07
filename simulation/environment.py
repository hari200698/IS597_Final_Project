import random
import uuid
import numpy as np
from typing import List, Dict, Any

def create_object_detection_simulation(num_objects=50, seed=42):
    """Create a simulation with randomly placed objects in a defined area.

    Args:
        num_objects: Number of objects to place in the simulation
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


    for _ in range(num_objects):
        obj_type = random.choices(object_types, weights=object_type_weights, k=1)[0]
        x_generator = lambda: (v if (v := random.uniform(-40, 150)) < -2.7 or v > 2.7 else x_generator())
        y_generator = lambda: (v if (v := random.uniform(-40, 40)) < -1 or v > 1 else y_generator())
        x = x_generator()
        y = y_generator()
        z = 1

        objects.append({
            'type': obj_type,
            'position': (x,y,z),
            'id': str(uuid.uuid4())  # Add unique ID for tracking
        })

    return objects
