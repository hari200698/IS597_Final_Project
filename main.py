import matplotlib.pyplot as plt
import numpy as np
from config.sensor_configs import create_sensor_config
from simulation.monte_carlo import run_monte_carlo_simulation_with_fusion
from visualization.plots import generate_all_plots


if __name__ == "__main__":
    config_types = ["tesla_vision", "mercedes_drive_pilot", "generic_av"]
    results_by_config = {}

    for config_type in config_types:
        print(f"\n=== MC for config: {config_type} ===")
        sensor_config = create_sensor_config(config_type)
        sensor_configs = []

        for name, config in sensor_config.items():
            sensor_configs.append({
                'name': name,
                'type': config['type'],
                'position': tuple(config['position']),
                'range': config['range'],
                'fov': config.get('field_of_view', config.get('horizontal_fov', 360)),
                'orientation': tuple(config['orientation'])
            })

        results = run_monte_carlo_simulation_with_fusion(
            sensor_configs=sensor_configs,
            num_objects=20,
            area_size=150,
            num_iterations=500,  # Fixed number of iterations
            environment_conditions={'fog_density': 0.1}
        )

        results_by_config[config_type] = results
        print(f"- Mean Detection Rate: {results['mean_detection_rate']:.2%}")
        print(f"- Mean Confidence Score: {results['mean_confidence_score']:.2f}")
        print(f"- Completed {results['iterations_run']} iterations")

    # Now you can plot the convergence manually using the individual_rates data
    plt.figure(figsize=(10, 6))

    for config, results in results_by_config.items():
        rates = results['individual_rates']
        iterations = range(1, len(rates) + 1)

        # Calculate cumulative moving average to visualize convergence
        cumulative_avg = np.cumsum(rates) / np.arange(1, len(rates) + 1)

        plt.plot(iterations, cumulative_avg, label=f"{config} (final: {results['mean_detection_rate']:.2%})")

    plt.title('Convergence of Detection Rates Over Iterations', fontsize=15)
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Cumulative Average Detection Rate', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Configuration')
    plt.savefig("convergence_plot.png", dpi=300, bbox_inches='tight')
    plt.show()

    # After running all simulations and collecting results_by_config
    generate_all_plots(results_by_config, save_dir="simulation_results")
