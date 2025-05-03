from typing import Dict, Any

def create_tesla_vision_config():
    """
    Creates a Tesla Vision sensor configuration (Model 3/Y) with camera-only setup.

    Returns:
        dict: A dictionary containing Tesla Vision sensor configurations
    """
    # Tesla Model 3/Y dimensions (in meters)
    vehicle_length = 4.7
    vehicle_width = 1.9
    vehicle_height = 1.5

    # Reference coordinate system:
    # - Origin (0,0,0) is at the center of the vehicle
    # - X-axis points forward (positive = front of vehicle)
    # - Y-axis points to the left side of the vehicle (when facing forward)
    # - Z-axis points upward

    # Tesla Vision camera configuration
    config = {
        # Three forward cameras in windshield housing
        "main_forward_camera": {
            "type": "camera",
            "position": [2.1, 0.0, 0.7],  # Center windshield, upper
            "orientation": [0, 0, 0],  # [roll, pitch, yaw] in degrees
            "field_of_view": 60,  # horizontal FOV in degrees
            "range": 150,  # in meters
            "resolution": [1280, 960]  # pixels
        },
        "forward_wide_camera": {
            "type": "camera",
            "position": [2.1, 0.0, 0.69],  # Center windshield, upper, same housing
            "orientation": [0, 0, 0],
            "field_of_view": 120,  # wider FOV
            "range": 60,
            "resolution": [1280, 960]
        },
        "forward_narrow_camera": {
            "type": "camera",
            "position": [2.1, 0.0, 0.71],  # Center windshield, upper, same housing
            "orientation": [0, 0, 0],
            "field_of_view": 35,  # narrow FOV for long range
            "range": 250,
            "resolution": [1280, 960]
        },

        # B-pillar cameras
        "left_b_pillar_camera": {
            "type": "camera",
            "position": [0.2, 0.95, 0.4],  # Left B-pillar
            "orientation": [0, 0, 90],  # facing left
            "field_of_view": 90,
            "range": 80,
            "resolution": [1280, 960]
        },
        "right_b_pillar_camera": {
            "type": "camera",
            "position": [0.2, -0.95, 0.4],  # Right B-pillar
            "orientation": [0, 0, -90],  # facing right
            "field_of_view": 90,
            "range": 80,
            "resolution": [1280, 960]
        },

        # Front fender cameras (rearward looking)
        "left_front_fender_camera": {
            "type": "camera",
            "position": [1.8, 0.95, 0.3],  # Left front fender
            "orientation": [0, 0, 125],  # angled backward on left side
            "field_of_view": 90,
            "range": 80,
            "resolution": [1280, 960]
        },
        "right_front_fender_camera": {
            "type": "camera",
            "position": [1.8, -0.95, 0.3],  # Right front fender
            "orientation": [0, 0, -125],  # angled backward on right side
            "field_of_view": 90,
            "range": 80,
            "resolution": [1280, 960]
        },

        # Rear camera
        "rear_camera": {
            "type": "camera",
            "position": [-2.35, 0.0, 0.4],  # Center rear, above license plate
            "orientation": [0, 0, 180],  # facing rear
            "field_of_view": 120,
            "range": 50,
            "resolution": [1280, 960]
        }
    }

    return config


def create_mercedes_drive_pilot_config():
    """
    Creates a Mercedes-Benz Drive Pilot sensor configuration (S-Class/EQS).

    Returns:
        dict: A dictionary containing Mercedes Drive Pilot sensor configurations
    """
    # Mercedes S-Class/EQS dimensions (in meters)
    vehicle_length = 5.2
    vehicle_width = 2.1
    vehicle_height = 1.5

    # Mercedes Drive Pilot sensor configuration
    config = {
        # Cameras
        "stereo_multipurpose_camera": {
            "type": "camera",
            "position": [2.4, 0.0, 0.7],  # Upper center of windshield
            "orientation": [0, 0, 0],
            "field_of_view": 120,
            "range": 180,
            "resolution": [1920, 1080]
        },
        "front_surround_camera": {
            "type": "camera",
            "position": [2.6, 0.0, 0.0],  # Front grille
            "orientation": [0, 0, 0],
            "field_of_view": 180,
            "range": 20,
            "resolution": [1280, 720]
        },
        "rear_surround_camera": {
            "type": "camera",
            "position": [-2.6, 0.0, 0.4],  # Trunk lid
            "orientation": [0, 0, 180],
            "field_of_view": 180,
            "range": 20,
            "resolution": [1280, 720]
        },
        "left_mirror_camera": {
            "type": "camera",
            "position": [0.8, 1.05, 0.3],  # Left side mirror
            "orientation": [0, 0, 90],
            "field_of_view": 180,
            "range": 20,
            "resolution": [1280, 720]
        },
        "right_mirror_camera": {
            "type": "camera",
            "position": [0.8, -1.05, 0.3],  # Right side mirror
            "orientation": [0, 0, -90],
            "field_of_view": 180,
            "range": 20,
            "resolution": [1280, 720]
        },

        # Radar systems
        "long_range_front_radar": {
            "type": "radar",
            "position": [2.6, 0.0, -0.3],  # Front bumper center
            "orientation": [0, 0, 0],
            "field_of_view": 60,
            "range": 250,
            "resolution": "high"
        },
        "front_left_corner_radar": {
            "type": "radar",
            "position": [2.5, 0.9, -0.3],  # Front bumper, left corner
            "orientation": [0, 0, 45],
            "field_of_view": 120,
            "range": 100,
            "resolution": "medium"
        },
        "front_right_corner_radar": {
            "type": "radar",
            "position": [2.5, -0.9, -0.3],  # Front bumper, right corner
            "orientation": [0, 0, -45],
            "field_of_view": 120,
            "range": 100,
            "resolution": "medium"
        },
        "rear_left_corner_radar": {
            "type": "radar",
            "position": [-2.5, 0.9, -0.3],  # Rear bumper, left corner
            "orientation": [0, 0, 135],
            "field_of_view": 120,
            "range": 100,
            "resolution": "medium"
        },
        "rear_right_corner_radar": {
            "type": "radar",
            "position": [-2.5, -0.9, -0.3],  # Rear bumper, right corner
            "orientation": [0, 0, -135],
            "field_of_view": 120,
            "range": 100,
            "resolution": "medium"
        },

        # Lidar system
        "front_lidar": {
            "type": "lidar",
            "position": [2.55, 0.0, -0.1],  # Front center, behind grille
            "orientation": [0, 0, 0],
            "vertical_fov": 30,
            "horizontal_fov": 120,
            "range": 200,
            "points_per_second": 1000000
        }
    }

    return config


def create_generic_av_config():
    """
    Creates a generic autonomous vehicle sensor configuration with a typical
    sensor suite including cameras, lidars, and radars.

    Returns:
        dict: A dictionary containing sensor configurations
    """
    # Base vehicle dimensions (in meters)
    vehicle_length = 4.5  # typical mid-size vehicle length
    vehicle_width = 1.5   # typical mid-size vehicle width
    vehicle_height = 1.5  # typical mid-size vehicle height

    # Sensor configuration
    config = {
        # Cameras
        "front_camera": {
            "type": "camera",
            "position": [2.1, 0.0, 0.75],  # Center windshield, upper
            "orientation": [0, 0, 0],
            "field_of_view": 120,
            "range": 150,
            "resolution": [1920, 1080]
        },

        # Lidar
        "roof_lidar": {
            "type": "lidar",
            "position": [0.0, 0.0, 0.75],  # Center roof
            "orientation": [0, 0, 0],
            "vertical_fov": 40,
            "horizontal_fov": 360,  # Full 360° coverage
            "range": 200,
            "points_per_second": 1200000
        },

        # Radars
        "front_radar": {
            "type": "radar",
            "position": [2.25, 0.0, -0.5],  # Front bumper center
            "orientation": [0, 0, 0],
            "field_of_view": 60,
            "range": 200,
            "resolution": "medium"
        },
        "rear_radar": {
            "type": "radar",
            "position": [-2.25, 0.0, -0.5],  # Rear bumper center
            "orientation": [0, 0, 180],
            "field_of_view": 60,
            "range": 150,
            "resolution": "medium"
        },
        "front_left_radar": {
            "type": "radar",
            "position": [2.1, 0.75, -0.5],  # Front left bumper/fender
            "orientation": [0, 0, 45],
            "field_of_view": 120,
            "range": 100,
            "resolution": "medium"
        },
        "front_right_radar": {
            "type": "radar",
            "position": [2.1, -0.75, -0.5],  # Front right bumper/fender
            "orientation": [0, 0, -45],
            "field_of_view": 120,
            "range": 100,
            "resolution": "medium"
        }
    }

    return config


def create_sensor_config(config_type="generic_av"):
    """
    Creates a sensor configuration with options for different vehicle types.

    Args:
        config_type (str): Configuration type - "generic_av" (default),
                          "tesla_vision", "mercedes_drive_pilot"

    Returns:
        dict: A dictionary containing sensor configurations
    """
    if config_type == "tesla_vision":
        return create_tesla_vision_config()
    elif config_type == "mercedes_drive_pilot":
        return create_mercedes_drive_pilot_config()
    else:  # generic_av is the default
        return create_generic_av_config()
