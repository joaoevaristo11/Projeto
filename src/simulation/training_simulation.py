import traci
import numpy as np
import random
import timeit
import os
import warnings

warnings.filterwarnings("ignore")
import src.simulation.intersection_manager as intersection_manager
import src.algorithms.sapa as sapa
import tensorflow as tf


class Simulation:
    def __init__(self, Model_1, Model_2, Memory_1, Memory_2, TrafficGen, PedestrianGen, sumo_cmd, gamma, max_steps,
                 green_duration, yellow_duration, num_states, num_actions, training_epochs):
        #network parameters
        self._Model_Cell_1 = Model_1
        self._Model_Cell_2 = Model_2
        self._Memory_1 = Memory_1
        self._Memory_2 = Memory_2
        self._TrafficGen = TrafficGen
        self._PedestrianGen = PedestrianGen
        self._gamma = gamma
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._training_epochs = training_epochs

        self._model_training_loss_cell_1 = []
        self._model_training_loss_cell_2 = []

        self._Pveh = 0.50
        self._Pped = 0.50

        self.intersections = intersection_manager.create_intersections(self._num_states)
        self.routes = intersection_manager.create_routes()
        self.waiting_ped = intersection_manager.create_waiting_zones()
        self.tl_names = intersection_manager.create_tl_names()
        self.incoming_roads = intersection_manager.create_incoming_routes()
        self.lanes_200_400 = intersection_manager.create_200_400_routes()
        self.map_env = intersection_manager.create_map_environment_()
        self.sapa = sapa.sapa_module()

    def run(self, episode, epsilon, train_ON_OFF):
        """
        Runs an episode of simulation, then starts a training session
        """
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        self._TrafficGen.generate_routefile(seed=episode)
        self._PedestrianGen.generate_ped_routefile(seed=episode)
        traci.start(self._sumo_cmd)

        print("Simulating...")

        # initiate metrics
        self._step = 0

        while self._step < self._max_steps:

            if self.intersections[0].dur == -1:
                for idx, C in self.intersections.items():
                    # obter estado atual
                    current_state = C.get_state(idx, self.waiting_ped[idx], self.routes, self.lanes_200_400, 0)

                    # tempos de espera
                    current_total_wait = C.collect_waiting_times(self.incoming_roads[idx])
                    ped_wait = C.pedestrians_WaitingTime(self.waiting_ped[idx])

                    # escolher nova ação
                    if idx < 5:
                        C.action = self._choose_action(current_state, epsilon, self._Model_Cell_1)
                    else:
                        C.action = self._choose_action(current_state, epsilon, self._Model_Cell_2)

                    # atualizar históricos
                    C.old_state = current_state
                    C.old_action = C.action
                    C.old_total_wait = current_total_wait
                    C.old_ped_wait = ped_wait

                    # avançar fase
                    C.dur, C.yellow = C.choose_phase(self._step, C.action, C.old_action, self.tl_names[idx], C.yellow, idx, self.routes, self.map_env, self.sapa)

            for idx, C in self.intersections.items():
                if C.dur == 0:
                    if C.yellow == 0:
                        current_state = C.get_state(idx, self.waiting_ped[idx], self.routes, self.lanes_200_400, C.old_action)
                        current_total_wait = C.collect_waiting_times(self.incoming_roads[idx])
                        ped_wait = C.pedestrians_WaitingTime(self.waiting_ped[idx])

                        reward = (self._Pveh * (C.old_total_wait - current_total_wait) + (
                                    C.old_ped_wait - ped_wait) * self._Pped)

                        # escolher próxima ação
                        if idx < 5:
                            C.action = self._choose_action(current_state, epsilon, self._Model_Cell_1)
                            self._Memory_1.add_sample((C.old_state, C.old_action, reward, current_state))
                        else:
                            C.action = self._choose_action(current_state, epsilon, self._Model_Cell_2)
                            self._Memory_2.add_sample((C.old_state, C.old_action, reward, current_state))

                        # atualizar histórico
                        C.old_state = current_state
                        C.old_action = C.action
                        C.old_total_wait = current_total_wait
                        C.old_ped_wait = ped_wait

                        if reward < 0:
                            C.sum_neg_reward += reward

                    # avançar fase
                    C.dur, C.yellow = C.choose_phase(self._step, C.action, C.old_action, self.tl_names[idx], C.yellow, idx, self.routes, self.map_env, self.sapa)

            for C in self.intersections.values():
                if C.dur > 0:
                    C.dur -= 1
            traci.simulationStep()
            self._step += 1

        self._save_episode_stats()
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)


        if train_ON_OFF == 1:
            print("Training...")
            start_time = timeit.default_timer()
            for index in range(self._training_epochs):
                self._replay(self._Model_Cell_1, self._model_training_loss_cell_1, self._Memory_1)
                self._replay(self._Model_Cell_2, self._model_training_loss_cell_2, self._Memory_2)
            self._Model_Cell_1.copy_weights()
            self._Model_Cell_2.copy_weights()
            training_time = round(timeit.default_timer() - start_time, 1)
        else:
            training_time = 0

        return simulation_time, training_time
    #fim de um ciclo de simulação

    def _choose_action(self, state, epsilon, model):
        """
        Decide wheter to perform an explorative or exploitative action, according to an epsilon-greedy policy
        """
        if random.random() < epsilon:
            return random.randint(0, self._num_actions - 1)  # random action
        else:
            return np.argmax(model.predict_one(state))  #the best action given the current state


    def _replay(self, Model, loss, memory):
        """
        Retrieve a group of samples from the memory and for each of them update the learning equation, then train
        """

        batch = memory.get_samples(Model.batch_size)
        batch_size = len(batch)

        if batch_size == 0:
            return

        # Extrair dados do batch
        states = np.array([b[0] for b in batch], dtype=np.float32)  # (batch_size, num_states)
        actions = np.array([b[1] for b in batch], dtype=np.int32)  # (batch_size,)
        rewards = np.array([b[2] for b in batch], dtype=np.float32)  # (batch_size,)
        next_states = np.array([b[3] for b in batch], dtype=np.float32)

        # Converter para tensores
        states_tf = tf.convert_to_tensor(states)
        next_states_tf = tf.convert_to_tensor(next_states)
        actions_tf = tf.convert_to_tensor(actions)
        rewards_tf = tf.convert_to_tensor(rewards)

        q_s_a = Model.model(states_tf)  # (batch_size, num_actions)

        # DDQN

        # escolher a ação com a rede principal
        q_next_online = Model.model(next_states_tf)
        next_actions = tf.argmax(q_next_online, axis=1)
        next_actions = tf.cast(next_actions, tf.int32)

        # avaliar com rede target
        q_next_target = Model.model_target(next_states_tf)

        indices_next = tf.stack([tf.range(batch_size), next_actions], axis=1)
        selected_q_next = tf.gather_nd(q_next_target, indices_next)

        # DDQN equation
        updates = rewards_tf + self._gamma * selected_q_next

        # Atualizar apenas Q(s,a) executado
        targets = tf.identity(q_s_a)
        indices = tf.stack([tf.range(batch_size), actions_tf], axis=1)
        targets = tf.tensor_scatter_nd_update(targets, indices, updates)

        # Treinar
        Model.train_batch(states_tf, targets)
        loss.append(Model.training_loss)


    def _save_episode_stats(self):
        """
        Save the stats of the episode to plot the graphs at the end of the session
        """
        for idx, C in self.intersections.items():
            # armazenar o reward negativo deste cruzamento no episódio
            C.reward_episode.append(C.sum_neg_reward)
            C.sum_neg_reward = 0

    @property
    def reward_stores(self):
        return {idx: C.reward_episode for idx, C in self.intersections.items()}

    @property
    def model_loss_cell_1(self):
        return self._model_training_loss_cell_1

    @property
    def model_loss_cell_2(self):
        return self._model_training_loss_cell_2
