import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from typing import Dict, List, Any, Optional


def visualize_sensor_positions(sensors, objects, area_size, detected_objects=None, save_path=None):
    """Visualize sensor positions and their detection areas.

    Args:
        sensors: List of sensor configurations
        objects: List of all objects in the simulation
        area_size: Size of the simulation area
        detected_objects: List of objects detected by sensors
        save_path: Path to save the visualization (None for display only)

    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot area boundaries
    ax.set_xlim(0, area_size)
    ax.set_ylim(0, area_size)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Create a set of detected object IDs for quick lookup
    detected_ids = set()
    if detected_objects:
        for det in detected_objects:
            detected_ids.add(det['object']['id'])

    # Plot objects
    for obj in objects:
        x, y = obj['position']
        width, length = obj['width'], obj['length']

        # Determine if object was detected
        was_detected = obj['id'] in detected_ids if detected_objects else False

        # Different colors based on object type and detection status
        if obj['type'] == 'pedestrian':
            color = 'green' if was_detected else 'darkgreen'
            marker = 'o'
            size = 25
        elif obj['type'] == 'vehicle':
            color = 'blue' if was_detected else 'darkblue'
            marker = 's'
            size = 50
        elif obj['type'] == 'cyclist':
            color = 'purple' if was_detected else 'indigo'
            marker = '^'
            size = 35
        else:  # static_obstacle
            color = 'gray' if was_detected else 'dimgray'
            marker = 'X'
            size = 40

        ax.scatter(x, y, c=color, marker=marker, s=size, alpha=0.8 if was_detected else 0.4)

    # Plot sensors and their detection ranges
    for i, sensor in enumerate(sensors):
        x, y, z = sensor['position']

        # Plot sensor
        ax.scatter(x, y, c='red', marker='*', s=150, zorder=10)
        ax.annotate(f"S{i+1}: {sensor['type']}", (x, y), xytext=(5, 5),
                     textcoords='offset points', color='red', fontweight='bold')

        # Plot detection range
        range_circle = plt.Circle((x, y), sensor['range'], fill=False,
                              color='red', linestyle='-', alpha=0.3)
        ax.add_patch(range_circle)

        # If sensor has a field of view (FOV), visualize it
        if 'fov' in sensor and sensor['fov'] < 360:
            # This would require more complex visualization using wedges
            # For simplicity, we'll just note it in the annotation
            ax.annotate(f"FOV: {sensor['fov']}°", (x, y), xytext=(5, -10),
                         textcoords='offset points', color='red')

    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Pedestrian (detected)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='darkgreen', markersize=10, alpha=0.4, label='Pedestrian (not detected)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', markersize=10, label='Vehicle (detected)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='darkblue', markersize=10, alpha=0.4, label='Vehicle (not detected)'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='purple', markersize=10, label='Cyclist (detected)'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='indigo', markersize=10, alpha=0.4, label='Cyclist (not detected)'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor='gray', markersize=10, label='Obstacle (detected)'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor='dimgray', markersize=10, alpha=0.4, label='Obstacle (not detected)'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor='red', markersize=15, label='Sensor'),
        Line2D([0], [0], color='red', alpha=0.3, label='Sensor Range')
    ]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
              ncol=3, fancybox=True, shadow=True)

    plt.title('Sensor Placement and Object Detection Visualization')
    plt.tight_layout()

    # Save or show the figure
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return None
    else:
        return fig

def generate_all_plots(results_by_config, save_dir=None):
    """
    Generate and optionally save visualization plots for sensor configuration comparison.
    
    Args:
        results_by_config: Dictionary mapping configuration names to their simulation results
        save_dir: Directory to save plots (None for display only)
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    
    # Create save directory if needed
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    configs = list(results_by_config.keys())
    
    # 1. Detection Rate Comparison
    plt.figure(figsize=(10, 6))
    
    rates = [results_by_config[c]['mean_detection_rate'] for c in configs]
    
    # Calculate standard deviation for error bars if available
    errors = []
    for c in configs:
        if 'individual_rates' in results_by_config[c]:
            rates_array = np.array(results_by_config[c]['individual_rates'])
            errors.append(np.std(rates_array))
        else:
            errors.append(0)
    
    bars = plt.bar(configs, rates, yerr=errors, capsize=10)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.2%}', ha='center', va='bottom')
    
    plt.title('Detection Rate by Sensor Configuration', fontsize=15)
    plt.ylabel('Detection Rate', fontsize=12)
    plt.xlabel('Configuration Type', fontsize=12)
    plt.ylim(0, max(rates) * 1.2)  # Add some space for error bars
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    if save_dir:
        plt.savefig(f"{save_dir}/detection_rate.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Object Type Detection Performance
    plt.figure(figsize=(12, 8))
    
    all_obj_types = set()
    for config in configs:
        if 'detection_by_type' in results_by_config[config]:
            all_obj_types.update(results_by_config[config]['detection_by_type'].keys())
    
    if all_obj_types:  # Only proceed if we have object types
        obj_types = sorted(list(all_obj_types))
        
        # Set up bar positions
        x = np.arange(len(obj_types))
        width = 0.8 / len(configs)  # Width of bars
        
        # Plot bars for each configuration
        for i, config in enumerate(configs):
            rates = []
            for obj_type in obj_types:
                if ('detection_by_type' in results_by_config[config] and
                    obj_type in results_by_config[config]['detection_by_type']):
                    rates.append(results_by_config[config]['detection_by_type'][obj_type]['rate'])
                else:
                    rates.append(0)
            
            offset = (i - len(configs)/2 + 0.5) * width
            plt.bar(x + offset, rates, width, label=config)
        
        plt.title('Detection Rate by Object Type', fontsize=15)
        plt.ylabel('Detection Rate', fontsize=12)
        plt.xlabel('Object Type', fontsize=12)
        plt.xticks(x, [t.capitalize() for t in obj_types])
        plt.legend(title='Configuration')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        if save_dir:
            plt.savefig(f"{save_dir}/object_type.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    # 3. Convergence Visualization
    plt.figure(figsize=(10, 6))
    
    for config, results in results_by_config.items():
        if 'individual_rates' in results and results['individual_rates']:
            rates = results['individual_rates']
            iterations = range(1, len(rates) + 1)
            
            # Calculate cumulative moving average
            cumulative_avg = np.cumsum(rates) / np.arange(1, len(rates) + 1)
            
            plt.plot(iterations, cumulative_avg, label=f"{config} (final: {results['mean_detection_rate']:.2%})")
    
    plt.title('Convergence of Detection Rates', fontsize=15)
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Cumulative Average Detection Rate', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Configuration')
    
    if save_dir:
        plt.savefig(f"{save_dir}/convergence.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. Confidence Score Distribution
    if any('mean_confidence_score' in results for results in results_by_config.values()):
        plt.figure(figsize=(10, 6))
        
        # Bar chart of mean confidence scores
        confidence_scores = [results.get('mean_confidence_score', 0) for results in results_by_config.values()]
        plt.bar(configs, confidence_scores)
        
        plt.title('Mean Confidence Score by Configuration', fontsize=15)
        plt.ylabel('Mean Confidence Score', fontsize=12)
        plt.xlabel('Configuration Type', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        if save_dir:
            plt.savefig(f"{save_dir}/confidence.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    # 5. Detection by Iteration (Line Plot)
    plt.figure(figsize=(12, 6))
    
    for config, results in results_by_config.items():
        if 'individual_rates' in results and results['individual_rates']:
            rates = results['individual_rates']
            iterations = range(1, len(rates) + 1)
            
            # Plot raw rates (with some smoothing if needed)
            window_size = min(10, len(rates))
            if window_size > 1:
                smoothed = np.convolve(rates, np.ones(window_size)/window_size, mode='valid')
                plt.plot(range(window_size, len(rates) + 1), smoothed, label=config)
            else:
                plt.plot(iterations, rates, label=config)
    
    plt.title('Detection Rate by Iteration', fontsize=15)
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Detection Rate', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Configuration')
    
    if save_dir:
        plt.savefig(f"{save_dir}/detection_by_iteration.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # 6. Radar Chart (if we have enough metrics)
    if all('detection_by_type' in results for results in results_by_config.values()):
        # Find common object types across all configs
        common_types = set.intersection(*[set(results['detection_by_type'].keys()) 
                                         for results in results_by_config.values()])
        
        if common_types and len(common_types) >= 2:  # Need at least a few metrics for radar chart
            metrics = ['Overall Detection'] + [f"{t.capitalize()}" for t in common_types]
            
            # Create figure
            plt.figure(figsize=(10, 8))
            ax = plt.subplot(111, polar=True)
            
            # Number of metrics
            N = len(metrics)
            
            # Compute angle for each metric
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Draw the chart for each configuration
            for i, config in enumerate(configs):
                values = [results_by_config[config]['mean_detection_rate']]
                
                # Add detection rates for each object type
                for obj_type in common_types:
                    values.append(results_by_config[config]['detection_by_type'][obj_type]['rate'])
                
                # Close the loop
                values += values[:1]
                
                # Plot
                ax.plot(angles, values, linewidth=2, label=config)
                ax.fill(angles, values, alpha=0.1)
            
            # Add labels
            plt.xticks(angles[:-1], metrics)
            
            # Add legend and title
            plt.legend(loc='upper right')
            plt.title('Sensor Configuration Performance Comparison', fontsize=15)
            
            if save_dir:
                plt.savefig(f"{save_dir}/radar.png", dpi=300, bbox_inches='tight')
            plt.show()
    
    # 7. Sensor Count Comparison (if available)
    if all('sensors' in results for results in results_by_config.values()):
        plt.figure(figsize=(10, 6))
        
        # Count sensors by type for each configuration
        sensor_counts = {}
        all_sensor_types = set()
        
        for config, results in results_by_config.items():
            if 'sensors' in results:
                sensor_counts[config] = {}
                for sensor in results['sensors']:
                    sensor_type = sensor['type']
                    all_sensor_types.add(sensor_type)
                    sensor_counts[config][sensor_type] = sensor_counts[config].get(sensor_type, 0) + 1
        
        if sensor_counts and all_sensor_types:
            # Convert to format suitable for stacked bar chart
            sensor_types = sorted(list(all_sensor_types))
            data = {sensor_type: [sensor_counts[config].get(sensor_type, 0) for config in configs] 
                    for sensor_type in sensor_types}
            
            # Create stacked bar chart
            bottom = np.zeros(len(configs))
            for sensor_type in sensor_types:
                plt.bar(configs, data[sensor_type], bottom=bottom, label=sensor_type.capitalize())
                bottom += np.array(data[sensor_type])
            
            plt.title('Sensor Count by Type and Configuration', fontsize=15)
            plt.ylabel('Number of Sensors', fontsize=12)
            plt.xlabel('Configuration Type', fontsize=12)
            plt.legend(title='Sensor Type')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            if save_dir:
                plt.savefig(f"{save_dir}/sensor_count.png", dpi=300, bbox_inches='tight')
            plt.show()