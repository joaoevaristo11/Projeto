from __future__ import absolute_import
from __future__ import print_function
import tensorflow as tf
import os
import datetime
import warnings
import argparse
from shutil import copyfile
warnings.filterwarnings("ignore")
from src.simulation.training_simulation import Simulation
from src.simulation.generator import TrafficGenerator
from src.simulation.ped_generator import PedestrianGenerator
from src.agents.memory import Memory
from src.agents.model import TrainModel
from src.utils.visualization import Visualization
from src.utils.utils import import_train_configuration, set_sumo, set_train_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train DDQN traffic control models')
    parser.add_argument('--config', type=str, default='config/training_settings.ini',
                        help='Path to configuration file')
    args = parser.parse_args()

    config = import_train_configuration(config_file=args.config)
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    path = set_train_path(config['models_path_name'])

    gpus = tf.config.list_physical_devices('GPU')
    print("GPUs disponíveis:", gpus)

    # ── Modelos de FASE ───────────────────────────────────────────────────────
    # ALTERADO: input_dim usa num_states_cell1/cell2 em vez de num_states único
    Model_Cell_1 = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states_cell1'],   # 170: J1/J3 (MT_* 2 lanes)
        output_dim=config['num_actions_phase']
    )
    Model_Cell_2 = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states_cell2'],   # 176: J2/J4 (510_* 3 lanes)
        output_dim=config['num_actions_phase']
    )

    # ── Modelo de DURAÇÃO ─────────────────────────────────────────────────────
    # ALTERADO: input_dim usa num_states_duration (sempre 170, igual para todos)
    Model_Duration = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states_duration'],  # 170: mesma dimensão para todos
        output_dim=config['num_actions_duration']
    )

    # ── Memórias ──────────────────────────────────────────────────────────────
    Memory_Cell_1   = Memory(config['memory_size_max'], config['memory_size_min'])
    Memory_Cell_2   = Memory(config['memory_size_max'], config['memory_size_min'])
    Memory_Duration = Memory(config['memory_size_max'], config['memory_size_min'])

    TrafficGen = TrafficGenerator(
        config['max_steps'],
        config['n_cars_generated'],
        config['scenario']
    )
    PedestrianGen = PedestrianGenerator(
        config['max_steps'],
        config['n_peds_generated']
    )
    Viz = Visualization(path, dpi=96)

    Sim = Simulation(
        Model_Cell_1,
        Model_Cell_2,
        Model_Duration,
        Memory_Cell_1,
        Memory_Cell_2,
        Memory_Duration,
        TrafficGen,
        PedestrianGen,
        sumo_cmd,
        config['gamma'],
        config['max_steps'],
        config['yellow_duration'],
        # ALTERADO: passa os três num_states separados em vez de um único
        config['num_states_cell1'],
        config['num_states_cell2'],
        config['num_states_duration'],
        config['num_actions_phase'],
        config['num_actions_duration'],
        config['training_epochs']
    )

    timestamp_start = datetime.datetime.now()

    print("\n----- Warm-up (3 episódios aleatórios)")
    for warm_up_ep in range(3):
        Sim.run(warm_up_ep, epsilon=1.0, train_ON_OFF=0)

    for episode in range(1, config['total_episodes'] + 1):
        print(f'\n----- Episode {episode} of {config["total_episodes"]}')
        epsilon = 1.0 - (episode / config['total_episodes'])
        simulation_time, training_time = Sim.run(episode, epsilon, train_ON_OFF=1)
        print(f'Simulation time: {simulation_time}s  |  Training time: {training_time}s  '
              f'|  Total: {round(simulation_time + training_time, 1)}s')

    print("\n----- Start time:", timestamp_start)
    print("----- End time:", datetime.datetime.now())
    print("----- Session info saved at:", path)

    Model_Cell_1.save_model(path, "Trained_Cell_1")
    Model_Cell_2.save_model(path, "Trained_Cell_2")
    Model_Duration.save_model(path, "Trained_Duration")

    copyfile(src='config/training_settings.ini',
             dst=os.path.join(path, 'training_settings.ini'))

    for idx, rewards in Sim.reward_stores.items():
        Viz.save_data_and_plot(
            data=rewards,
            filename=f"Reward_C{idx}",
            xlabel='Episode',
            ylabel=f'Cumulative negative reward of C{idx}'
        )

    Viz.save_data_and_plot(data=Sim.model_loss_cell_1,   filename='MSE Loss Cell 1',   xlabel='Episode', ylabel='Loss')
    Viz.save_data_and_plot(data=Sim.model_loss_cell_2,   filename='MSE Loss Cell 2',   xlabel='Episode', ylabel='Loss')
    Viz.save_data_and_plot(data=Sim.model_loss_duration, filename='MSE Loss Duration', xlabel='Episode', ylabel='Loss')