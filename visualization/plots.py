import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from typing import Dict, List, Any, Optional

def visualize_fog_effects(config_types=["tesla_vision", "mercedes_drive_pilot", "generic_av"], 
                          fog_levels=[0.0, 0.3, 0.6, 0.9], num_iterations=1000):
    """
    Visualize the effect of fog on different sensor configurations
    """
    results = {}
    
    for config_type in config_types:
        fog_results = []
        sensor_config = create_sensor_config(config_type)
        sensor_configs = []
        
        # Convert sensor config to list format
        for name, config in sensor_config.items():
            sensor_dict = {
                'name': name,
                'type': config['type'],
                'position': tuple(config['position']),
                'range': config['range'],
                'fov': config.get('field_of_view', config.get('horizontal_fov', 120)),
                'orientation': tuple(config['orientation'])
            }
            
            # Add sensor-specific parameters
            if config['type'] == 'lidar' and 'k' in config:
                sensor_dict['k'] = config['k']
                
            if config['type'] == 'radar':
                if 'a' in config:
                    sensor_dict['a'] = config['a']
                if 'd0' in config:
                    sensor_dict['d0'] = config['d0']
                    
            sensor_configs.append(sensor_dict)
        
        # Run simulation with different fog levels
        for fog_density in fog_levels:
            print(f"Running {config_type} with fog density {fog_density}")
            result = run_monte_carlo_simulation_with_fusion(
                sensor_configs=sensor_configs,
                num_objects=20,
                num_iterations=num_iterations,
                environment_conditions={'fog_density': fog_density}
            )
            
            # Calculate sensor type percentages
            sensor_type_percentages = {}
            sensor_type_detections = result.get('sensor_type_detections', {})
            total_detections = sum(sensor_type_detections.values())
            
            if total_detections > 0:
                for s_type in sensor_type_detections:
                    sensor_type_percentages[s_type] = sensor_type_detections[s_type] / total_detections
            
            fog_results.append({
                'fog_density': fog_density,
                'detection_rate': result['mean_detection_rate'],
                'sensor_type_detections': sensor_type_detections,
                'sensor_type_percentages': sensor_type_percentages
            })
            
        results[config_type] = fog_results
    
    # Plot overall detection rates
    plt.figure(figsize=(12, 6))
    
    for config_type, fog_results in results.items():
        fog_densities = [r['fog_density'] for r in fog_results]
        detection_rates = [r['detection_rate'] for r in fog_results]
        
        plt.plot(fog_densities, detection_rates, 'o-', linewidth=2, 
                 label=f"{config_type}")
    
    plt.title('Effect of Fog Density on Detection Rate', fontsize=15)
    plt.xlabel('Fog Density', fontsize=12)
    plt.ylabel('Detection Rate', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Configuration')
    plt.savefig("fog_effect_overall.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    
    return results
