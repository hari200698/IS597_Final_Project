import numpy as np
from typing import Dict, List, Any
from ..simulation.detection import sensor_fusion_detection
from ..simulation.environment import create_object_detection_simulation


def run_monte_carlo_simulation_with_fusion(sensor_configs, num_objects=50, area_size=150,
                                           num_iterations=100,
                                           seed=42, environment_conditions=None):
    """
    Run a fixed number of Monte Carlo simulation iterations using sensor fusion for detection decisions.

    Args:
        sensor_configs: List of sensor configurations
        num_objects: Number of objects per simulation
        area_size: Size of simulation area
        num_iterations: Fixed number of iterations to run
        seed: Base random seed
        environment_conditions: Environmental conditions affecting detection

    Returns:
        Dict containing results and statistics
    """
    if environment_conditions is None:
        environment_conditions = {'fog_density': 0.0}

    detection_rates = []
    detection_by_type = {}
    object_type_totals_per_iter = {}
    confidence_scores = []
    all_iteration_data = []  # Store data from each iteration for detailed analysis

    # Run for fixed number of iterations
    for i in range(num_iterations):
        iter_seed = seed + i

        # Create simulation objects for this iteration
        objects = create_object_detection_simulation(num_objects, area_size, seed=iter_seed)
        last_iteration_objects = objects if i == num_iterations - 1 else None

        # Initialize counts for object types for THIS iteration
        current_iter_type_counts = {}
        for obj in objects:
            obj_type = obj['type']
            current_iter_type_counts[obj_type] = current_iter_type_counts.get(obj_type, 0) + 1
            if obj_type not in object_type_totals_per_iter:
                 object_type_totals_per_iter[obj_type] = 0
            object_type_totals_per_iter[obj_type] += 1

        # Run detection with sensor fusion for this iteration
        detected_this_iter = set()
        detected_by_type_this_iter = {}
        iter_confidence_scores = []
        iter_detections = []  # Store individual detection results

        # Process each object with all sensors at once (fusion approach)
        for obj in objects:
            # Create a list of objects excluding the current target to prevent self-occlusion
            other_objects = [o for o in objects if o['id'] != obj['id']]

            is_detected, confidence, sensor_probs = sensor_fusion_detection(
                sensor_configs, obj, other_objects, environment_conditions
            )

            # Store detection result
            iter_detections.append({
                'object_id': obj['id'],
                'object_type': obj['type'],
                'detected': is_detected,
                'confidence': confidence,
                'sensor_probabilities': sensor_probs
            })

            if is_detected:
                detected_this_iter.add(obj['id'])
                obj_type = obj['type']
                detected_by_type_this_iter[obj_type] = detected_by_type_this_iter.get(obj_type, 0) + 1
                iter_confidence_scores.append(confidence)

        # Calculate detection rate for this iteration
        detection_rate = len(detected_this_iter) / num_objects if num_objects > 0 else 0
        detection_rates.append(detection_rate)

        # Store average confidence score for detected objects
        avg_confidence = sum(iter_confidence_scores) / len(iter_confidence_scores) if iter_confidence_scores else 0
        confidence_scores.append(avg_confidence)

        # Update cumulative detection counts by type
        for obj_type, count in detected_by_type_this_iter.items():
             if obj_type not in detection_by_type:
                 detection_by_type[obj_type] = {'total': 0, 'detected': 0}
             detection_by_type[obj_type]['detected'] += count

        # Store data for this iteration
        all_iteration_data.append({
            'iteration': i,
            'detection_rate': detection_rate,
            'confidence_score': avg_confidence,
            'detections_by_type': detected_by_type_this_iter.copy(),
            'total_by_type': current_iter_type_counts.copy(),
            'detailed_detections': iter_detections
        })

    # Calculate final statistics
    mean_detection_rate = np.mean(detection_rates)
    mean_confidence = np.mean(confidence_scores) if confidence_scores else 0

    # Finalize detection rate by object type
    final_detection_by_type = {}
    for obj_type, counts in detection_by_type.items():
         total_instances_of_type = object_type_totals_per_iter.get(obj_type, 0)
         detected_count = counts['detected']
         rate = detected_count / total_instances_of_type if total_instances_of_type > 0 else 0.0
         final_detection_by_type[obj_type] = {
             'total': total_instances_of_type,
             'detected': detected_count,
             'rate': rate
         }

    return {
        'mean_detection_rate': mean_detection_rate,
        'mean_confidence_score': mean_confidence,
        'iterations_run': num_iterations,
        'individual_rates': detection_rates,
        'individual_confidences': confidence_scores,
        'detection_by_type': final_detection_by_type,
        'sensors': sensor_configs,
        'objects': last_iteration_objects,
        'total_objects': num_objects,
        'objects_detected': int(mean_detection_rate * num_objects),
        'detection_rate': mean_detection_rate,
        'all_iteration_data': all_iteration_data  # Include detailed data for each iteration
    }
