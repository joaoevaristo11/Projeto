import traci
import numpy as np
import timeit
import src.simulation.intersection_manager as intersection_manager
import src.algorithms.sapa as sapa

PHASE_TO_ACTION = {
    0: 1,   # NS green
    3: 2,   # EW green
}

Volume_Lanes = [
    'MT_NS_1', 'MT_SN_1', 'EG_WE_1', 'EG_EW_1',
    '510_NS_1', '510_SN_1', 'VV_WE_1', 'VV_EW_1',
]


class Simulation:
    def __init__(self, Model_1, Model_2, TrafficGen, PedestrianGen, sumo_cmd, max_steps,
                 yellow_duration, num_states, num_actions, network, n_agents):
        self.eye = None
        self._Model_Cell_1 = Model_1
        self._Model_Cell_2 = Model_2
        self._TrafficGen = TrafficGen
        self._PedestrianGen = PedestrianGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        #self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._type_Network = network
        self._n_agents = n_agents

        self.intersections = intersection_manager.create_intersections(self._num_states)
        for C in self.intersections.values():
            #C.green_duration = self._green_duration
            C.yellow_duration = self._yellow_duration
        self.routes         = intersection_manager.create_routes()
        self.waiting_ped    = intersection_manager.create_waiting_zones()
        self.tl_names       = intersection_manager.create_tl_names()
        self.incoming_roads = intersection_manager.create_incoming_routes()
        self.lanes_110_132  = intersection_manager.create_110_132_routes()
        self.map_env        = intersection_manager.create_map_environment_()
        self.sapa           = sapa.sapa_module()

        self._veiculos_unicos = {lane_id: set() for lane_id in Volume_Lanes}
        self._volume_por_lane = {lane_id: 0     for lane_id in Volume_Lanes}
        self._minute = 1
        self._real_offsets = {1: 0, 2: 1, 3: 1, 4: 0}

    def _is_real_mode(self):
        return str(self._type_Network).upper() in ('REAL', 'BASELINE', 'FIXED')

    def _real_action_for_step(self, idx):
        cycle = 60
        return ((self._step // cycle) + self._real_offsets.get(idx, 0)) % 2

    def _get_model(self, idx):
        return self._Model_Cell_1 if idx in (1, 3) else self._Model_Cell_2

    def run(self, episode):
        start_time = timeit.default_timer()
        self._TrafficGen.generate_routefile(seed=episode)
        self._PedestrianGen.generate_ped_routefile(seed=episode)
        print("Using the", self._type_Network, "algorithm for testing")
        traci.start(self._sumo_cmd)
        print("Simulating...")

        while self._step < self._max_steps:
            if self._step % 300 == 0:
                print(f"[testing] step {self._step}/{self._max_steps}")

            for idx, C in self.intersections.items():

                if self._is_real_mode():
                    # Modo REAL: alternância cíclica NS/WE sem rede neuronal
                    C.action = self._real_action_for_step(idx)
                    C.set_green_phase(C.action, self.tl_names[idx])
                    if C.old_action != C.action:
                        C.n_times_active[C.action] += 1
                    C.phase_duration[C.action] += 1
                    C.old_action = C.action

                else:
                    # Modo inteligente: rede neuronal
                    if C.dur == 0 or C.dur == -1:
                        if C.yellow == 0:
                            current_state = C.get_state(idx, self.waiting_ped[idx], self.routes, self.lanes_110_132, C.old_action)
                            model = self._get_model(idx)
                            C.action = self._choose_action(current_state, idx, model)
                        C.dur, C.yellow = C.choose_phase(self._step, C.action, C.old_action, self.tl_names[idx], C.yellow, idx, self.routes, self.map_env, self.sapa)
                        C.old_action = C.action
                        if C.dur != 4:
                            C.phase_duration[C.action] += C.dur
                            C.n_times_active[C.action] += 1
                    if C.dur > 0:
                        C.dur -= 1

                self._allactions(C.phase_activated, C.id, self.incoming_roads[idx], self.waiting_ped[idx])
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
        return round(timeit.default_timer() - start_time, 1)

    def _veh_volumes(self):
        for lane_id in Volume_Lanes:
            novos = set(traci.edge.getLastStepVehicleIDs(lane_id)) - self._veiculos_unicos[lane_id]
            if novos:
                self._volume_por_lane[lane_id] += len(novos)
                self._veiculos_unicos[lane_id].update(novos)

    def _time_extension(self, C):
        if self._step % 300 == 0:
            for phase_id in range(self._num_actions):
                avg = C.phase_duration[phase_id] / C.n_times_active[phase_id] if C.n_times_active[phase_id] > 0 else 0
                C.phase_durations[phase_id + 1].append(avg)
        else:
            for phase_id in range(self._num_actions):
                C.phase_extension_1_hour[phase_id + 1] = (
                    C.phase_duration[phase_id] / C.n_times_active[phase_id]
                    if C.n_times_active[phase_id] > 0 else 0
                )

    def _vehicles_med_Speed(self, incoming_roads, avg_speed, avg_speed_greenArea):
        speed = sum(traci.edge.getLastStepMeanSpeed(e) for e in incoming_roads)
        avg_speed.append(speed / len(incoming_roads))
        if self._minute == 60:
            avg_speed_greenArea.append(sum(avg_speed) / self._minute)
            avg_speed.clear()

    def _haltingPerson(self, waiting_zones, ped_halting):
        count = sum(
            1 for lane in waiting_zones[0]
            for pid in traci.edge.getLastStepPersonIDs(lane)
            if traci.person.getSpeed(pid) < 0.1
        )
        ped_halting.append(count)

    def _allactions(self, lista, tl, incoming_roads, ped_edges):
        for i in range(min(4, len(incoming_roads))):
            ped_list  = traci.edge.getLastStepPersonIDs(ped_edges[0][i]) if i < len(ped_edges[0]) else []
            cars_list = traci.edge.getLastStepVehicleIDs(incoming_roads[i])
            if len(cars_list) > 0 or len(ped_list) > 0:
                phase  = traci.trafficlight.getPhase(tl)
                action = PHASE_TO_ACTION.get(phase)
                if action is not None:
                    lista.append(action)
                return

    def _collect_waiting_times(self, incoming_roads, waitingVeh, awt_greenArea):
        total = sum(
            traci.edge.getWaitingTime(e) / (1 + traci.edge.getLastStepHaltingNumber(e))
            for e in incoming_roads
        )
        waitingVeh.append(total / len(incoming_roads))
        if self._minute == 60:
            awt_greenArea.append(sum(waitingVeh) / self._minute)
            waitingVeh.clear()

    def _choose_action(self, state, idx, model):
        if self._type_Network == 'DQN':
            return np.argmax(model.predict_one(state))
        else:
            agent_pos = idx - 1
            obs = state.astype(np.float32)[None, :]
            oh  = self.eye[agent_pos][None, :]
            a, _, _ = model.actor.act(obs=obs, agent_onehot=oh, deterministic=True)
            return int(a[0])

    def _get_queue_length(self, idx, queue):
        queue.append(sum(traci.edge.getLastStepHaltingNumber(r) for r in self.incoming_roads[idx]))

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