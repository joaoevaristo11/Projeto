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
    # Cell_1: partilhado por J1 e J3 (cruzamentos Av. Marquês de Tomar)
    Model_Cell_1 = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states'],
        output_dim=config['num_actions_phase']   # 2 ações: NS ou EW
    )
    # Cell_2: partilhado por J2 e J4 (cruzamentos Av. 5 de Outubro)
    Model_Cell_2 = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states'],
        output_dim=config['num_actions_phase']   # 2 ações: NS ou EW
    )

    # ── Modelo de DURAÇÃO ─────────────────────────────────────────────────────
    # Partilhado por todos os cruzamentos.
    # Recebe o estado local (mesma dimensão para todos) e escolhe duração do verde.
    Model_Duration = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states'],
        output_dim=config['num_actions_duration']  # 4 ações: 8s, 16s, 24s, 32s
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
        config['num_states'],
        config['num_actions_phase'],
        config['num_actions_duration'],
        config['training_epochs']
    )

    timestamp_start = datetime.datetime.now()

    # ── Warm-up (3 episódios aleatórios antes do treino) ──────────────────────
    print("\n----- Warm-up (3 episódios aleatórios)")
    for warm_up_ep in range(3):
        Sim.run(warm_up_ep, epsilon=1.0, train_ON_OFF=0)

    # ── Treino principal ──────────────────────────────────────────────────────
    for episode in range(1, config['total_episodes'] + 1):
        print(f'\n----- Episode {episode} of {config["total_episodes"]}')
        epsilon = 1.0 - (episode / config['total_episodes'])
        simulation_time, training_time = Sim.run(episode, epsilon, train_ON_OFF=1)
        print(f'Simulation time: {simulation_time}s  |  Training time: {training_time}s  '
              f'|  Total: {round(simulation_time + training_time, 1)}s')

    print("\n----- Start time:", timestamp_start)
    print("----- End time:", datetime.datetime.now())
    print("----- Session info saved at:", path)

    # ── Guardar modelos ───────────────────────────────────────────────────────
    Model_Cell_1.save_model(path, "Trained_Cell_1")
    Model_Cell_2.save_model(path, "Trained_Cell_2")
    Model_Duration.save_model(path, "Trained_Duration")

    copyfile(src='config/training_settings.ini',
             dst=os.path.join(path, 'training_settings.ini'))

    # ── Gráficos de reward ────────────────────────────────────────────────────
    for idx, rewards in Sim.reward_stores.items():
        Viz.save_data_and_plot(
            data=rewards,
            filename=f"Reward_C{idx}",
            xlabel='Episode',
            ylabel=f'Cumulative negative reward of C{idx}'
        )

    # ── Gráficos de loss ──────────────────────────────────────────────────────
    Viz.save_data_and_plot(
        data=Sim.model_loss_cell_1,
        filename='MSE Loss Cell 1',
        xlabel='Episode',
        ylabel='Loss'
    )
    Viz.save_data_and_plot(
        data=Sim.model_loss_cell_2,
        filename='MSE Loss Cell 2',
        xlabel='Episode',
        ylabel='Loss'
    )
    Viz.save_data_and_plot(
        data=Sim.model_loss_duration,
        filename='MSE Loss Duration',
        xlabel='Episode',
        ylabel='Loss'
    )