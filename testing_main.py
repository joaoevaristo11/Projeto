from __future__ import absolute_import
from __future__ import print_function

import os
import argparse
from shutil import copyfile

from src.simulation.testing_simulation import Simulation
from src.simulation.generator import TrafficGenerator
from src.simulation.ped_generator import PedestrianGenerator
from src.agents.model import TestModel
from src.utils.visualization import Visualization
from src.utils.utils import import_test_configuration, set_sumo, set_test_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test trained DDQN models')
    parser.add_argument('--config', type=str, default='config/testing_settings.ini',
                        help='Path to configuration file')
    args = parser.parse_args()

    config = import_test_configuration(config_file=args.config)
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    network = config['network']
    real_mode = str(network).upper() in ('REAL', 'BASELINE', 'FIXED')

    if real_mode:
        model_path = None
        plot_path = os.path.join(
            os.getcwd(),
            config['models_path_name'],
            'real_env',
            f"test_{config['episode_seed']}",
            ''
        )
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    else:
        model_path, plot_path = set_test_path(
            config['models_path_name'],
            config['model_to_test'],
            config['episode_seed']
        )

    # ── Carregar modelos ou None em modo REAL ─────────────────────────────────
    if real_mode:
        Model_Cell_1   = None
        Model_Cell_2   = None
        Model_Duration = None
    else:
        Model_Cell_1 = TestModel(
            input_dim=config['num_states_cell1'],   # 84
            model_path=model_path,
            name="Trained_Cell_1.h5"
        )
        Model_Cell_2 = TestModel(
            input_dim=config['num_states_cell2'],   # 124
            model_path=model_path,
            name="Trained_Cell_2.h5"
        )
        # DESATIVADO: carregar modelo de duração
        # Model_Duration = TestModel(
        #     input_dim=config['num_states_duration'],  # 170
        #     model_path=model_path,
        #     name="Trained_Duration.h5"
        # )
        Model_Duration = None  # substituído por duração fixa (16s) na simulation

    TrafficGen = TrafficGenerator(
        config['max_steps'],
        config['n_cars_generated'],
        config['scenario']
    )
    PedestrianGen = PedestrianGenerator(
        config['max_steps'],
        config['n_peds_generated']
    )
    Visualization = Visualization(plot_path, dpi=96)

    Simulation = Simulation(
        Model_Cell_1,
        Model_Cell_2,
        Model_Duration,      # None — Cell_Duration desativada
        TrafficGen,
        PedestrianGen,
        sumo_cmd,
        config['max_steps'],
        config['yellow_duration'],
        config['num_states_cell1'],      # 84
        config['num_states_cell2'],      # 124
        config['num_states_duration'],   # mantido no config mas não usado
        config['num_actions_phase'],
        config['num_actions_duration'],
        config['network'],
        config['n_agents']
    )

    print('\n----- Test episode')
    simulation_time = Simulation.run(config['episode_seed'])
    print('Simulation time:', simulation_time, 's')
    print("----- Testing info saved at:", plot_path)

    copyfile(src=args.config, dst=os.path.join(plot_path, 'testing_settings.ini'))

    for idx, data in Simulation.queue_stores.items():
        Visualization.save_data_and_plot(data=data, filename=f'Queue_{idx}',
            xlabel='Step', ylabel=f'Queue length at C{idx} (vehicles)')

    for idx, data in Simulation.ped_halting_stores.items():
        Visualization.save_data_and_plot(data=data, filename=f'Pedestrian Halting C{idx}',
            xlabel='Time (s)', ylabel=f'Pedestrian Halting at C{idx} (Pedestrians)')

    for idx, data in Simulation.phase_stores.items():
        Visualization.save_data_and_plot(data=data, filename=f'Agent Actions C{idx}',
            xlabel='Time (s)', ylabel=f'Phases activated at C{idx}')

    for idx, data in Simulation.avg_speed_stores.items():
        Visualization.save_data_and_plot(data=data, filename=f'Average Vehicle Speed C{idx}',
            xlabel='Time (s)', ylabel=f'Average Vehicle Speed at C{idx} (m/s)')

    for idx, data in Simulation.awt_stores.items():
        Visualization.save_data_and_plot(data=data, filename=f'Average Waiting Time C{idx}',
            xlabel='Time (s)', ylabel=f'Average Waiting Time at C{idx} (s)')

    for idx, data in Simulation.phase_times_1h_stores.items():
        Visualization.save_data_and_barchart(data=data, filename=f'Average Phase Time in C{idx}',
            xlabel='Phase', ylabel=f'Average Phase Time at C{idx} (s)')

    Visualization.save_data_and_barchart(
        data=list(Simulation.vol_lanes.values()),
        filename='Lane Volume',
        xlabel='Lane id',
        ylabel='Volume of vehicles (veh/h)'
    )

    if not real_mode:
        for idx, phase_logs in Simulation.duration_log_stores.items():
            for phase_id, durations in phase_logs.items():
                phase_name = "NS" if phase_id == 0 else "EW"
                Visualization.save_data_and_plot(
                    data=durations,
                    filename=f'Duration Log C{idx} {phase_name}',
                    xlabel='Decision',
                    ylabel=f'Green duration chosen at C{idx} {phase_name} (s)'
                )