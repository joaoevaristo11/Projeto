import traci
import numpy as np
import random
import timeit
import warnings

warnings.filterwarnings("ignore")
import src.simulation.intersection_manager as intersection_manager
import tensorflow as tf
from src.agents.intersection import DURATION_VALUES, decode_action, NUM_ACTIONS_COMBINED


class Simulation:
    def __init__(self, Model_Cell_1, Model_Cell_2, Model_Duration,
                 Memory_1, Memory_2, Memory_Duration,
                 TrafficGen, PedestrianGen, sumo_cmd, gamma, max_steps,
                 yellow_duration,
                 num_states_cell1, num_states_cell2, num_states_duration,
                 num_actions_phase, num_actions_duration,
                 training_epochs):

        self._Model_Cell_1 = Model_Cell_1
        self._Model_Cell_2 = Model_Cell_2
        # Model_Duration e Memory_Duration ignorados: decisão de duração
        # está integrada na ação combinada (Opção C)

        self._Memory_1 = Memory_1
        self._Memory_2 = Memory_2

        self._TrafficGen    = TrafficGen
        self._PedestrianGen = PedestrianGen
        self._gamma         = gamma
        self._step          = 0
        self._sumo_cmd      = sumo_cmd
        self._max_steps     = max_steps
        self._yellow_duration = yellow_duration
        self._num_states_cell1 = num_states_cell1   # 93  para J1/J3
        self._num_states_cell2 = num_states_cell2   # 135 para J2/J4
        self._num_actions_phase = num_actions_phase  # 2 — usado para logging por fase
        self._training_epochs   = training_epochs

        self._model_training_loss_cell_1 = []
        self._model_training_loss_cell_2 = []

        self._Pveh = 0.75
        self._Pped = 0.25

        self.intersections = intersection_manager.create_intersections({
            1: self._num_states_cell1,   # J1 → Cell_1 → 93
            2: self._num_states_cell2,   # J2 → Cell_2 → 135
            3: self._num_states_cell1,   # J3 → Cell_1 → 93
            4: self._num_states_cell2,   # J4 → Cell_2 → 135
        })
        for C in self.intersections.values():
            C.yellow_duration = self._yellow_duration
        self.routes         = intersection_manager.create_routes()
        self.waiting_ped    = intersection_manager.create_waiting_zones()
        self.tl_names       = intersection_manager.create_tl_names()
        self.incoming_roads = intersection_manager.create_incoming_routes()
        self.lanes_110_132  = intersection_manager.create_110_132_routes()
        self.map_env        = intersection_manager.create_map_environment_()

    # ── Utilitários ─────────────────────────────────────────────────────────

    def _get_phase_model_and_memory(self, idx):
        """Cell_1 para J1/J3; Cell_2 para J2/J4."""
        if idx in (1, 3):
            return self._Model_Cell_1, self._Memory_1
        else:
            return self._Model_Cell_2, self._Memory_2

    def _choose_action(self, state, epsilon, model, num_actions):
        if random.random() < epsilon:
            return random.randint(0, num_actions - 1)
        return int(np.argmax(model.predict_one(state)))

    # ── Loop principal ───────────────────────────────────────────────────────

    def run(self, episode, epsilon, train_ON_OFF):
        start_time = timeit.default_timer()

        self._TrafficGen.generate_routefile(seed=episode)
        self._PedestrianGen.generate_ped_routefile(seed=episode)
        traci.start(self._sumo_cmd)

        print("Simulating...")
        self._step = 0

        while self._step < self._max_steps:

            # ── Inicialização no primeiro step ───────────────────────
            if self.intersections[1].dur == -1:
                for idx, C in self.intersections.items():
                    phase_model, _ = self._get_phase_model_and_memory(idx)

                    current_state = C.get_state(idx, self.waiting_ped[idx], self.routes,
                                                self.lanes_110_132, 0)
                    ped_wait = C.pedestrians_WaitingTime(self.waiting_ped[idx])

                    C.action = self._choose_action(current_state, epsilon,
                                                   phase_model, NUM_ACTIONS_COMBINED)
                    phase, green_dur = decode_action(C.action)

                    C.old_state      = current_state
                    C.old_action     = C.action
                    C.old_total_wait = 0
                    C.old_ped_wait   = ped_wait

                    dur_yellow, C.yellow = C.choose_phase(
                        self._step, phase, -1, self.tl_names[idx], C.yellow)
                    C.dur = green_dur

            # ── Step normal ──────────────────────────────────────────
            for idx, C in self.intersections.items():
                if C.dur == 0:
                    if C.yellow == 0:
                        phase_model, phase_memory = self._get_phase_model_and_memory(idx)

                        current_state = C.get_state(idx, self.waiting_ped[idx], self.routes,
                                                    self.lanes_110_132, C.old_action)
                        current_total_wait = C.collect_waiting_times(self.incoming_roads[idx])
                        ped_wait = C.pedestrians_WaitingTime(self.waiting_ped[idx])

                        reward = (self._Pveh * (C.old_total_wait - current_total_wait)
                                  + self._Pped * (C.old_ped_wait - ped_wait))

                        C.action = self._choose_action(current_state, epsilon,
                                                       phase_model, NUM_ACTIONS_COMBINED)

                        phase_memory.add_sample((C.old_state, C.old_action, reward, current_state))

                        C.old_state      = current_state
                        C.old_action     = C.action
                        C.old_total_wait = current_total_wait
                        C.old_ped_wait   = ped_wait

                        if reward < 0:
                            C.sum_neg_reward += reward

                    phase, green_dur = decode_action(C.action)
                    old_phase = decode_action(C.old_action)[0] if C.old_action != -1 else -1

                    dur_yellow, C.yellow = C.choose_phase(
                        self._step, phase, old_phase, self.tl_names[idx], C.yellow)
                    C.dur = dur_yellow if C.yellow == 1 else green_dur

            for C in self.intersections.values():
                if C.dur > 0:
                    C.dur -= 1
            traci.simulationStep()
            self._step += 1

        self._save_episode_stats()
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        # ── Treino ──────────────────────────────────────────────────
        if train_ON_OFF == 1:
            print("Training...")
            start_time = timeit.default_timer()
            for _ in range(self._training_epochs):
                self._replay(self._Model_Cell_1, self._model_training_loss_cell_1, self._Memory_1)
                self._replay(self._Model_Cell_2, self._model_training_loss_cell_2, self._Memory_2)
            self._Model_Cell_1.copy_weights()
            self._Model_Cell_2.copy_weights()
            training_time = round(timeit.default_timer() - start_time, 1)
        else:
            training_time = 0

        return simulation_time, training_time

    # ── DDQN replay ─────────────────────────────────────────────────────────

    def _replay(self, Model, loss, memory):
        batch = memory.get_samples(Model.batch_size)
        batch_size = len(batch)
        if batch_size == 0:
            return

        states      = np.array([b[0] for b in batch], dtype=np.float32)
        actions     = np.array([b[1] for b in batch], dtype=np.int32)
        rewards     = np.array([b[2] for b in batch], dtype=np.float32)
        next_states = np.array([b[3] for b in batch], dtype=np.float32)

        states_tf      = tf.convert_to_tensor(states)
        next_states_tf = tf.convert_to_tensor(next_states)
        actions_tf     = tf.convert_to_tensor(actions)
        rewards_tf     = tf.convert_to_tensor(rewards)

        q_s_a = Model.model(states_tf)

        q_next_online   = Model.model(next_states_tf)
        next_actions    = tf.cast(tf.argmax(q_next_online, axis=1), tf.int32)
        q_next_target   = Model.model_target(next_states_tf)
        indices_next    = tf.stack([tf.range(batch_size), next_actions], axis=1)
        selected_q_next = tf.gather_nd(q_next_target, indices_next)

        updates = rewards_tf + self._gamma * selected_q_next

        targets = tf.identity(q_s_a)
        indices = tf.stack([tf.range(batch_size), actions_tf], axis=1)
        targets = tf.tensor_scatter_nd_update(targets, indices, updates)

        Model.train_batch(states_tf, targets)
        loss.append(Model.training_loss)

    # ── Stats ────────────────────────────────────────────────────────────────

    def _save_episode_stats(self):
        for C in self.intersections.values():
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