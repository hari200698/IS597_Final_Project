import numpy as np
from typing import Dict, List, Tuple, Any

def calculate_detection_probability(sensor, obj, visibility_factor=1.0):
    """
    Calculates detection probability for a given sensor-object pair, incorporating:
    - FOV and range checks.
    - Sensor-specific probability decay (camera: binary, lidar: exponential, radar: sigmoid).
    - Sensor noise.
    - Sensor dropout.
    - Environmental conditions (fog).
    """
    # Extract positions
    sx, sy, sz = sensor['position']
    tx, ty, tz = obj['position']

    # --- Basic Geometry Check ---
    distance = np.sqrt((sx - tx)**2 + (sy - ty)**2 + (sz - tz)**2)

    if distance > sensor['range']:
        return 0.0

    # Field of view check
    if 'fov' in sensor and sensor['fov'] < 360:
      # Calculate horizontal angle (azimuth)
      horizontal_angle = math.degrees(math.atan2(ty - sy, tx - sx))
      sensor_yaw = sensor['orientation'][2]
      relative_horizontal = horizontal_angle - sensor_yaw

      # Normalize to -180 to 180
      while relative_horizontal > 180:
          relative_horizontal -= 360
      while relative_horizontal < -180:
          relative_horizontal += 360

      # Check horizontal FOV
      if abs(relative_horizontal) > sensor['fov'] / 2:
          return 0.0

      # Calculate vertical angle (elevation)
      # We need the horizontal distance for this
      horizontal_distance = math.sqrt((tx - sx)**2 + (ty - sy)**2)
      vertical_angle = math.degrees(math.atan2(tz - sz, horizontal_distance))

      # Get sensor pitch (if available, otherwise assume 0)
      sensor_pitch = sensor['orientation'][1] if len(sensor['orientation']) > 1 else 0
      relative_vertical = vertical_angle - sensor_pitch

      # Normalize to -90 to 90 (vertical angles are between -90 and 90 degrees)
      if relative_vertical > 90:
          relative_vertical = 180 - relative_vertical
      elif relative_vertical < -90:
          relative_vertical = -180 - relative_vertical

      # Check vertical FOV (if defined, otherwise use a default or derived value)
      vertical_fov = sensor.get('vertical_fov', sensor['fov'] / 2)  # Default: half of horizontal FOV

      if abs(relative_vertical) > vertical_fov / 2:
          return 0.0
    # --- Base Detection Probability by Sensor Type ---
    sensor_type = sensor['type'].lower()

    # Default value in case parameters are missing
    detection_prob = 1.0

    if sensor_type == 'camera':
        # Cameras: Binary detection if within range/FOV
        detection_prob = 1.0

    elif sensor_type == 'lidar':
        # Lidar: Exponential decay with distance
        k = sensor.get('k', 0.01)  # Default decay rate if not specified
        detection_prob = np.exp(-k * distance)

    elif sensor_type == 'radar':
        # Radar: Sigmoid decay with distance
        a = sensor.get('a', 0.1)     # Steepness parameter
        d0 = sensor.get('d0', sensor['range'] * 0.8)  # Midpoint at 80% of range by default
        detection_prob = 1 / (1 + np.exp(a * (distance - d0)))

    else:
        # Default for unknown sensor types
        detection_prob = 1.0

    # --- Apply Fog Effects ---
    # Get fog density from global environment_conditions
    # This is a workaround since we can't modify the function signature
    global environment_conditions
    if 'environment_conditions' in globals() and environment_conditions is not None:
        fog_density = environment_conditions.get('fog_density', 0.0)
    else:
        fog_density = 0.0

    if fog_density > 0:
        # Convert fog_density (0-1) to meteorological extinction coefficient (β)
        # Based on Gultepe et al. (2007)
        # Light fog (0.2): visibility ~1000m (β=0.003)
        # Moderate fog (0.5): visibility ~300m (β=0.01)
        # Heavy fog (0.8): visibility ~100m (β=0.03)
        # Very dense fog (1.0): visibility ~50m (β=0.06)
        
        # Meteorological extinction coefficient (β) calculation
        beta_vis = 0.003 + 0.057 * fog_density**2  # Nonlinear relationship

        # Apply Beer-Lambert law for fog attenuation based on sensor type
        if sensor_type == 'camera':
            # Cameras severely affected by fog (Hasirlioglu & Riener, 2020)
            camera_factor = 1.0  # Full effect
            fog_attenuation = np.exp(-beta_vis * camera_factor * distance)
            detection_prob *= fog_attenuation
            
        elif sensor_type == 'lidar':
            # Lidar moderately affected by fog (Bijelic et al., 2018)
            # 905nm wavelength (common in automotive)
            lidar_factor = 0.7  # 70% of visual extinction
            fog_attenuation = np.exp(-beta_vis * lidar_factor * distance)
            detection_prob *= fog_attenuation
            
        elif sensor_type == 'radar':
            # Radar minimally affected by fog (Brooker, 2007)
            # 77GHz automotive radar
            radar_factor = 0.05  # Only 5% of visual extinction
            fog_attenuation = np.exp(-beta_vis * radar_factor * distance)
            detection_prob *= fog_attenuation

    # Clip to [0,1] (just in case numerical errors push it outside)
    detection_prob = max(0.0, min(1.0, detection_prob * visibility_factor))

    # --- Sensor Noise (Gaussian) ---
    # Bar-Shalom et al. 2001: Zero-mean Gaussian noise typical
    if sensor_type == 'camera':
        sigma = 0.03
    elif sensor_type == 'lidar':
        sigma = 0.05
    elif sensor_type == 'radar':
        sigma = 0.02
    else:
        sigma = 0.04  # default

    noise = np.random.normal(0, sigma)
    detection_prob += noise

    detection_prob = max(0.0, min(1.0, detection_prob))

    # --- Sensor Dropout (Bernoulli) ---
    dropout_rates = {
        'camera': 0.001,
        'lidar': 0.005,
        'radar': 0.0005
    }

    dropout_chance = dropout_rates.get(sensor_type, 0.002)

    if random.random() < dropout_chance:
        detection_prob = 0.0

    return detection_prob
