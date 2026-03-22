import traci
import numpy as np
import random
import timeit
import os

import src.simulation.intersection_manager as intersection_manager
import src.algorithms.sapa as sapa

PHASE_TO_ACTION = {
    0: 1,   # NS_FD
    2: 2,   # N_ALL
    4: 3,   # S_ALL
    6: 4,   # NS_Left
    8: 5,   # WE_FD
    10: 6,  # W_ALL
    12: 7,  # E_ALL
    14: 8,  # WE_LEFT
    32: 9   # Pedestrians
}

# Edges externos de entrada da rede — usados para contagem de volumes
# Um edge por entrada de cada artéria
Volume_Lanes = [
    'MT_NS_1',    # Av. Marquês de Tomar — entrada Norte
    'MT_SN_1',    # Av. Marquês de Tomar — entrada Sul
    'EG_WE_1',    # Av. Elias Garcia — entrada Oeste
    'EG_EW_1',    # Av. Elias Garcia — entrada Este
    '510_NS_1',   # Av. 5 de Outubro — entrada Norte
    '510_SN_1',   # Av. 5 de Outubro — entrada Sul
    'VV_WE_1',    # Av. Visconde de Valmor — entrada Oeste
    'VV_EW_1',    # Av. Visconde de Valmor — entrada Este
]


class Simulation:
    def __init__(self, Model_1, Model_2, TrafficGen, PedestrianGen, sumo_cmd, max_steps, green_duration,
                 yellow_duration, num_states, num_actions, network, n_agents):
        self.eye = None
        self._Model_Cell_1 = Model_1  # J1 e J3 (cruzamentos Av. Marquês de Tomar)
        self._Model_Cell_2 = Model_2  # J2 e J4 (cruzamentos Av. 5 de Outubro)
        self._TrafficGen = TrafficGen
        self._PedestrianGen = PedestrianGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions

        self._type_Network = network
        self._n_agents = n_agents

        self.intersections = intersection_manager.create_intersections(self._num_states)
        self.routes = intersection_manager.create_routes()
        self.waiting_ped = intersection_manager.create_waiting_zones()
        self.tl_names = intersection_manager.create_tl_names()
        self.incoming_roads = intersection_manager.create_incoming_routes()
        self.lanes_110_132 = intersection_manager.create_110_132_routes()
        self.map_env = intersection_manager.create_map_environment_()
        self.sapa = sapa.sapa_module()

        self._veiculos_unicos = {lane_id: set() for lane_id in Volume_Lanes}
        self._volume_por_lane = {lane_id: 0 for lane_id in Volume_Lanes}

        self._minute = 1

    def _get_model(self, idx):
        """
        - J1 (idx=1) e J3 (idx=3): cruzamentos Av. Marquês de Tomar → Model Cell 1
        - J2 (idx=2) e J4 (idx=4): cruzamentos Av. 5 de Outubro    → Model Cell 2
        """
        if idx in (1, 3):
            return self._Model_Cell_1
        else:  # idx in (2, 4)
            return self._Model_Cell_2

    def run(self, episode):
        """
        Runs the testing simulation
        """
        start_time = timeit.default_timer()

        self._TrafficGen.generate_routefile(seed=episode)
        self._PedestrianGen.generate_ped_routefile(seed=episode)

        if self._type_Network == 'MAPPO':
            print("Using the", self._type_Network, "algorithm for testing")
            self.eye = np.eye(self._n_agents, dtype=np.float32)
        else:
            print("Using the", self._type_Network, "algorithm for testing")

        traci.start(self._sumo_cmd)
        print("Simulating...")

        while self._step < self._max_steps:

            for idx, C in self.intersections.items():
                if C.dur == 0 or C.dur == -1:
                    if C.yellow == 0:
                        current_state = C.get_state(idx, self.waiting_ped[idx], self.routes, self.lanes_110_132, C.old_action)
                        model = self._get_model(idx)
                        C.action = self._choose_action(current_state, idx, model)

                    C.dur, C.yellow = C.choose_phase(self._step, C.action, C.old_action, self.tl_names[idx], C.yellow, idx, self.routes, self.map_env, self.sapa)
                    C.old_action = C.action

                    if C.dur != 4:  # dont count yellow phases
                        C.phase_duration[C.action] += C.dur
                        C.n_times_active[C.action] += 1

                self._allactions(C.phase_activated, C.id, self.incoming_roads[idx], self.waiting_ped[idx])

                if C.dur > 0:
                    C.dur -= 1

                self._get_queue_length(idx, C.queue_length)
                self._collect_waiting_times(self.incoming_roads[idx], C.waitingVeh, C.awt_greenArea)
                self._vehicles_med_Speed(self.incoming_roads[idx], C.avgspeed, C.avgspeed_greenArea)
                self._haltingPerson(self.waiting_ped[idx], C.pedestrians_halting)

                if (self._step == self._max_steps - 1 or self._step % 300 == 0) and self._step != 0:
                    self._time_extension(C)

                self._veh_volumes()

            traci.simulationStep()
            self._step += 1

            if self._minute == 60:
                self._minute = 0
            self._minute += 1

        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)
        return simulation_time

    def _veh_volumes(self):
        for lane_id in Volume_Lanes:
            veiculos_na_lane_agora = set(traci.edge.getLastStepVehicleIDs(lane_id))
            veiculos_ja_vistos = self._veiculos_unicos[lane_id]
            novos_veiculos = veiculos_na_lane_agora.difference(veiculos_ja_vistos)
            num_novos = len(novos_veiculos)
            if num_novos > 0:
                self._volume_por_lane[lane_id] += num_novos
                self._veiculos_unicos[lane_id].update(novos_veiculos)

    def _time_extension(self, C):
        """The Average Time given to each Phase by the SAPA block in each intersection"""
        if self._step % 300 == 0:
            for phase_id in range(9):
                if C.n_times_active[phase_id] > 0:
                    avg_duration = C.phase_duration[phase_id] / C.n_times_active[phase_id]
                else:
                    avg_duration = 0
                C.phase_durations[phase_id + 1].append(avg_duration)
        else:
            for phase_id in range(9):
                if C.n_times_active[phase_id] > 0:
                    C.phase_extension_1_hour[phase_id + 1] = C.phase_duration[phase_id] / C.n_times_active[phase_id]
                else:
                    C.phase_extension_1_hour[phase_id + 1] = 0

    def _vehicles_med_Speed(self, incoming_roads, avg_speed, avg_speed_greenArea):
        """Average Speed of vehicles for each intersection (m/s) per minute"""
        speed = 0
        for edge in incoming_roads:
            speed += traci.edge.getLastStepMeanSpeed(edge)
        avg_speed.append(speed / len(incoming_roads))
        if self._minute == 60:
            avg_speed_greenArea.append(sum(avg_speed) / self._minute)
            avg_speed.clear()

    def _haltingPerson(self, waiting_zones, ped_halting):
        """Number of pedestrians halting in waiting areas per intersection"""
        count = 0
        for lane in waiting_zones[0]:
            persons = traci.edge.getLastStepPersonIDs(lane)
            for pid in persons:
                if traci.person.getSpeed(pid) < 0.1:
                    count += 1
        ped_halting.append(count)

    def _allactions(self, lista, tl, incoming_roads, ped_edges):
        """List of active phases by the agents in each intersection"""
        # usa os primeiros 4 edges de incoming_roads (N, S, E, W)
        for i in range(min(4, len(incoming_roads))):
            ped_list = traci.edge.getLastStepPersonIDs(ped_edges[0][i]) if i < len(ped_edges[0]) else []
            cars_list = traci.edge.getLastStepVehicleIDs(incoming_roads[i])
            if len(cars_list) > 0 or len(ped_list) > 0:
                phase = traci.trafficlight.getPhase(tl)
                action = PHASE_TO_ACTION.get(phase)
                if action is not None:
                    lista.append(action)
                return

    def _collect_waiting_times(self, incoming_roads, waitingVeh, awt_greenArea):
        """Retrieve the waiting time of every car in the incoming roads"""
        average_wt_edge = 0
        for edge in incoming_roads:
            wt = traci.edge.getWaitingTime(edge)
            halted = traci.edge.getLastStepHaltingNumber(edge)
            average_wt_edge += wt / (1 + halted)
        mean_step_wait = average_wt_edge / len(incoming_roads)
        waitingVeh.append(mean_step_wait)
        if self._minute == 60:
            awt_greenArea.append(sum(waitingVeh) / self._minute)
            waitingVeh.clear()

    def _choose_action(self, state, idx, model):
        """Pick the best action based on the current state"""
        if self._type_Network == 'DQN':
            return np.argmax(model.predict_one(state))
        else:
            # MAPPO: remap idx 1-4 para 0-3 para o one-hot
            agent_pos = idx - 1
            obs = state.astype(np.float32)[None, :]
            oh = self.eye[agent_pos][None, :]
            a, _, _ = model.actor.act(obs=obs, agent_onehot=oh, deterministic=True)
            return int(a[0])

    def _get_queue_length(self, idx, queue):
        """Retrieve the number of cars with speed = 0 in every incoming lane"""
        roads = self.incoming_roads[idx]
        queue_length = sum(traci.edge.getLastStepHaltingNumber(road) for road in roads)
        queue.append(queue_length)

    @property
    def queue_stores(self):
        return {idx: C.queue_length for idx, C in self.intersections.items()}

    @property
    def phase_stores(self):
        return {idx: C.phase_activated for idx, C in self.intersections.items()}

    @property
    def ped_halting_stores(self):
        return {idx: C.pedestrians_halting for idx, C in self.intersections.items()}

    @property
    def avg_speed_stores(self):
        return {idx: C.avgspeed_greenArea for idx, C in self.intersections.items()}

    @property
    def awt_stores(self):
        return {idx: C.awt_greenArea for idx, C in self.intersections.items()}

    @property
    def phase_times_1h_stores(self):
        return {idx: C.phase_extension_1_hour for idx, C in self.intersections.items()}

    @property
    def phase_times_5min_stores(self):
        return {idx: C.phase_durations for idx, C in self.intersections.items()}

    @property
    def vol_lanes(self):
        return self._volume_por_lane