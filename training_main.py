from __future__ import absolute_import
from __future__ import print_function
import tensorflow as tf
import os
import datetime
import warnings
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

    config = import_train_configuration(config_file='config/training_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    path = set_train_path(config['models_path_name'])

    gpus = tf.config.list_physical_devices('GPU')
    print("GPUs disponíveis:", gpus)

    Model_Cell_1 = TrainModel(
        config['num_layers'], 
        config['width_layers'], 
        config['batch_size'], 
        config['learning_rate'], 
        input_dim=config['num_states'], 
        output_dim=config['num_actions']
    )

    Model_Cell_2 = TrainModel(
        config['num_layers'],
        config['width_layers'],
        config['batch_size'],
        config['learning_rate'],
        input_dim=config['num_states'],
        output_dim=config['num_actions']
    )

    Memory_Cell_1 = Memory(
        config['memory_size_max'], 
        config['memory_size_min']
    )

    Memory_Cell_2 = Memory(
        config['memory_size_max'],
        config['memory_size_min']
    )

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
        path, 
        dpi=96
    )
        
    Simulation = Simulation(
        Model_Cell_1,
        Model_Cell_2,
        Memory_Cell_1,
        Memory_Cell_2,
        TrafficGen,
        PedestrianGen,
        sumo_cmd,
        config['gamma'],
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['num_states'],
        config['num_actions'],
        config['training_epochs']
    )
    
    episode = 1
    warm_up_eps = 0
    timestamp_start = datetime.datetime.now()

    while episode < config['total_episodes']:

        # Warm-up
        for warm_up_eps in range(3):
            simulation_time, training_time = Simulation.run(warm_up_eps, 1.0, 0)

        # Treino principal
        for episode in range(1, config['total_episodes'] + 1):
            print('\n----- Episode', episode, 'of', str(config['total_episodes']))
            epsilon = 1.0 - (episode / config['total_episodes'])
            simulation_time, training_time = Simulation.run(episode, epsilon, 1)
            print('Simulation time:', simulation_time, 's - Training time:', training_time, 's - Total:', round(simulation_time+training_time, 1), 's')


    print("\n----- Start time:", timestamp_start)
    print("----- End time:", datetime.datetime.now())
    print("----- Session info saved at:", path)

    Model_Cell_1.save_model(path, "Trained_Cell_1")
    Model_Cell_2.save_model(path, "Trained_Cell_2")

    copyfile(src='config/training_settings.ini', dst=os.path.join(path, 'training_settings.ini'))

    for idx, rewards in Simulation.reward_stores.items():
        filename = f"Reward_C{idx}"
        Visualization.save_data_and_plot(
            data=rewards,
            filename=filename,
            xlabel='Episode',
            ylabel=f'Cumulative negative reward of C{idx}'
        )

    Visualization.save_data_and_plot(data=Simulation.model_loss_cell_1, filename='MSE Loss Cell 1', xlabel='Episode', ylabel='Loss')
    Visualization.save_data_and_plot(data=Simulation.model_loss_cell_2, filename='MSE Loss Cell 2', xlabel='Episode', ylabel='Loss')

