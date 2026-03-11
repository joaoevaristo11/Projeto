from __future__ import absolute_import
from __future__ import print_function

import os
from shutil import copyfile

from src.simulation.testing_simulation import Simulation
from src.simulation.generator import TrafficGenerator
from src.simulation.ped_generator import PedestrianGenerator
from src.agents.model import TestModel
from src.utils.visualization import Visualization
from src.utils.utils import import_test_configuration, set_sumo, set_test_path


if __name__ == "__main__":

    config = import_test_configuration(config_file='config/testing_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    model_path, plot_path = set_test_path(config['models_path_name'], config['model_to_test'], config['episode_seed'])
    network = config['network']

    #if network == 'DQN':
    Model_Cell_1 = TestModel(
        input_dim=config['num_states'],
        model_path=model_path,
        name="Trained_Cell_1.h5"
    )
    Model_Cell_2 = TestModel(
        input_dim=config['num_states'],
        model_path=model_path,
        name="Trained_Cell_2.h5"
    )
    # else:
    #     n_agents = config['n_agents']
    #     Model = MAPPOAgent(
    #         obs_dim=config['num_states'],
    #         agent_id_dim=n_agents,  # one-hot de agente
    #         n_actions=config['num_actions'],
    #         lr=0.0  # não treinamos em teste
    #     )

    TrafficGen = TrafficGenerator(
        config['max_steps'],
        config['n_cars_generated'],
        config['scenario']
    )

    PedestrianGen = PedestrianGenerator(
        config['max_steps'],
        config['n_peds_generated']
    )

    Visualization = Visualization(
        plot_path,
        dpi=96
    )

    Simulation = Simulation(
        Model_Cell_1,
        Model_Cell_2,
        TrafficGen,
        PedestrianGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['num_states'],
        config['num_actions'],
        config['network'],
        config['n_agents']
    )

    print('\n----- Test episode')
    simulation_time = Simulation.run(config['episode_seed'])  # run the simulation
    print('Simulation time:', simulation_time, 's')

    print("----- Testing info saved at:", plot_path)

    copyfile(src='config/testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

    for idx, data in Simulation.queue_stores.items():
        Visualization.save_data_and_plot(
            data=data,
            filename=f'Queue_{idx}',
            xlabel='Step',
            ylabel=f'Queue length at C{idx}(vehicles)'
        )

    for idx, data in Simulation.ped_halting_stores.items():
        Visualization.save_data_and_plot(
            data=data,
            filename=f'Pedestrian Halting C{idx}',
            xlabel='Time (s)',
            ylabel=f'Pedestrian Halting at C{idx}(Pedestrians)'
        )

    for idx, data in Simulation.phase_stores.items():
        Visualization.save_data_and_plot(
            data=data,
            filename=f'Agent Actions C{idx}',
            xlabel='Time (s)',
            ylabel=f'Phases activated at C{idx}'
        )

    for idx, data in Simulation.avg_speed_stores.items():
        Visualization.save_data_and_plot(
            data=data,
            filename=f'Average Vehicle Speed C{idx}',
            xlabel='Time (s)',
            ylabel=f'Average Vehicle Speed at C{idx} (m/s)'
        )

    for idx, data in Simulation.awt_stores.items():
        Visualization.save_data_and_plot(
            data=data,
            filename=f'Average Waiting Time C{idx}',
            xlabel='Time (s)',
            ylabel=f'Average Waiting Time at C{idx} (m/s)'
        )

    for idx, data in Simulation.phase_times_1h_stores.items():
        Visualization.save_data_and_barchart(
            data=data,
            filename=f"Average Phase Time in C{idx}",
            xlabel='Phase',
            ylabel=f'Average Phase Time at C{idx} (s)'
        )

    volumes = list(Simulation.vol_lanes.values())

    Visualization.save_data_and_barchart(
        data=volumes,
        filename=f'Lane Volume',
        xlabel='Lane id',
        ylabel=f'Volume of vehicles (veh/h) (m/s)'
    )

    # for idx, data in Simulation.phase_times_5min_stores.items():
    #     if idx == 0:
    #         Visualization.save_data_and_plot(
    #             data=data[idx],
    #             filename=f"Phase extension in 5minute window in C{idx}",
    #             xlabel='Phase',
    #             ylabel=f'Average Phase Time at C{idx} (s)'
    #         )



