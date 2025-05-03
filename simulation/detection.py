import numpy as np
from typing import Dict, List, Tuple, Any

def check_line_of_sight(sensor_pos, target_pos, objects, fog_density=0):
    """
    Check if there is a clear line of sight between sensor and target,
    first using an expanded 2D bounding-box test to skip distant objects.

    Args:
        sensor_pos: (x, y, z) position of the sensor
        target_pos: (x, y) position of the target object (z assumed elsewhere)
        objects:   List of all objects in the simulation (each with 'position', 'width', 'length')
        fog_density: Fog density factor (0 = clear, 1 = max fog)

    Returns:
        (is_visible: bool, visibility_factor: float)
    """
    sx, sy, sz = sensor_pos
    tx, ty     = target_pos

    # Quick AABB filter ---------------------------------------------------
    # Compute segment AABB in 2D
    min_x, max_x = sorted((sx, tx))
    min_y, max_y = sorted((sy, ty))

    # Expand by the largest object "radius" (half of width+length)/2
    # We divide by 4 because width+length gives diameter*2; half of that is (w+l)/4
    max_size = max((obj['width'] + obj['length']) / 4 for obj in objects)

    min_x -= max_size
    max_x += max_size
    min_y -= max_size
    max_y += max_size

    # Precompute segment vector
    dx, dy = tx - sx, ty - sy
    seg_len = np.hypot(dx, dy)
    if seg_len == 0:
        # degenerate case: sensor and target coincide
        return True, 1.0

    ux, uy = dx / seg_len, dy / seg_len

    # 2) Detailed occlusion only for objects in the box -----------------------
    for obj in objects:
        ox, oy = obj['position']

        # Skip the target itself - using a small epsilon for floating point comparison
        # Alternatively, if objects have IDs, compare those instead
        epsilon = 1e-6
        if abs(ox - tx) < epsilon and abs(oy - ty) < epsilon:
            continue

        # AABB cull
        if not (min_x <= ox <= max_x and min_y <= oy <= max_y):
            continue

        # Project object center onto the segment (scalar projection)
        vx, vy = ox - sx, oy - sy
        proj = vx * ux + vy * uy

        # Only consider if projection falls onto the segment
        if proj < 0 or proj > seg_len:
            continue

        # Closest point on the line
        cx = sx + proj * ux
        cy = sy + proj * uy

        # Distance from object center to that closest point
        dist_to_line = np.hypot(cx - ox, cy - oy)

        # Use this specific object's radius rather than the maximum
        obj_radius = (obj['width'] + obj['length']) / 4

        if dist_to_line < obj_radius:
            # blocked
            return False, 0.0

    # 3) No occlusion found – compute visibility factor -----------------------
    # Straight-line distance (2D)
    distance = seg_len

    visibility_factor = 1.0
    if fog_density > 0:
        visibility_factor *= np.exp(-fog_density * distance / 100)

    return True, visibility_factor

def calculate_detection_probability(sensor, obj, visibility_factor=1.0):
    """Calculate probability of detecting an object based on sensor capabilities and conditions.

    Args:
        sensor: Sensor data including type, range, etc.
        obj: Object data including position, dimensions
        visibility_factor: Factor representing visibility conditions (0-1)

    Returns:
        float: Probability of detection between 0-1
    """
    # Extract positions
    sx, sy, sz = sensor['position']
    tx, ty = obj['position']

    # Calculate distance
    distance = np.sqrt((sx - tx)**2 + (sy - ty)**2)

    # If beyond max range, no detection possible
    if distance > sensor['range']:
        return 0.0

    # Base probability calculated using a sigmoid curve for more realistic drop-off
    # 1.0 at close range, gradually decreasing toward max range
    normalized_distance = distance / sensor['range']
    midpoint = 0.7  # Position of 0.5 probability
    steepness = 8  # Controls how quickly probability drops

    base_prob = 1.0 / (1.0 + np.exp(steepness * (normalized_distance - midpoint)))

    # Apply sensor type-specific factors
    if sensor['type'] == 'camera':
        # Cameras are affected more by visibility conditions
        prob = base_prob * visibility_factor**1.5
    elif sensor['type'] == 'lidar':
        # LiDAR is less affected by visibility but still impacted
        prob = base_prob * np.sqrt(visibility_factor)
    elif sensor['type'] == 'radar':
        # Radar is least affected by visibility conditions
        prob = base_prob * visibility_factor**0.25
    else:
        prob = base_prob * visibility_factor

    # Different object types have different detection probabilities
    if obj['type'] == 'pedestrian':
        # Pedestrians are smaller and harder to detect
        prob *= 0.9
    elif obj['type'] == 'vehicle':
        # Vehicles are larger and easier to detect
        prob *= 1.1
    elif obj['type'] == 'cyclist':
      prob *= 0.85
    elif obj['type'] == 'static_obstacle':
      prob *= 0.5

    # Ensure probability is between 0 and 1
    return max(0.0, min(1.0, prob))


def sensor_fusion_detection(sensors, obj,all_objects, environment_conditions=None):
    """
    Determine if an object is detected using fuzzy logic sensor fusion.

    Args:
        sensors: List of sensor configurations
        obj: Object to detect
        environment_conditions: Dict of environmental conditions

    Returns:
        tuple: (is_detected, confidence, sensor_probabilities)
    """
    if environment_conditions is None:
        environment_conditions = {'fog_density': 0.0}

    # Step 1: Calculate individual sensor detection probabilities
    sensor_probs = {}
    for sensor in sensors:
        # Check for line of sight considering occlusions
        has_los, visibility_factor = check_line_of_sight(
            sensor['position'],
            obj['position'],
            all_objects,
            environment_conditions.get('fog_density', 0.0)
        )

        if not has_los:
            sensor_probs[sensor['name']] = 0.0
            continue

        # Calculate detection probability
        detection_prob = calculate_detection_probability(sensor, obj, visibility_factor)
        sensor_probs[sensor['name']] = detection_prob

    # Step 2: Fuzzification - Convert probabilities to fuzzy membership values
    fuzzy_memberships = {}
    for sensor_name, prob in sensor_probs.items():
        # Define membership in "Detected" and "Not Detected" fuzzy sets
        fuzzy_memberships[sensor_name] = {
            'detected': prob,
            'not_detected': 1.0 - prob
        }

    # Step 3: Apply fuzzy rules
    # Rule 1: If any sensor has high detection probability, object is likely detected
    # Rule 2: If multiple sensors have medium detection probability, object is likely detected
    # Rule 3: If all sensors have low detection probability, object is likely not detected

    # Calculate rule strengths
    high_detection_strength = max([m['detected'] for m in fuzzy_memberships.values()], default=0)

    # For Rule 2 - Consider average of top 2 sensors if available
    sorted_probs = sorted([m['detected'] for m in fuzzy_memberships.values()], reverse=True)
    multi_sensor_strength = sum(sorted_probs[:2])/2 if len(sorted_probs) >= 2 else 0

    low_detection_strength = min([m['not_detected'] for m in fuzzy_memberships.values()], default=1)

    # Step 4: Combine rule outputs
    # Weight the rules based on their importance
    rule_weights = {
        'high_detection': 0.5,      # Weight for rule 1
        'multi_sensor': 0.4,        # Weight for rule 2
        'low_detection': 0.1        # Weight for rule 3
    }

    # Calculate final fuzzy confidence score
    detection_confidence = (
        high_detection_strength * rule_weights['high_detection'] +
        multi_sensor_strength * rule_weights['multi_sensor'] +
        (1 - low_detection_strength) * rule_weights['low_detection']
    )

    # Step 5: Defuzzification - Convert to binary decision
    # Use a threshold to determine final detection
    detection_threshold = 0.6  # Adjust based on preferred sensitivity
    is_detected = detection_confidence >= detection_threshold

    return is_detected, detection_confidence, sensor_probs
