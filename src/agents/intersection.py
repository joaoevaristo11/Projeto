import traci
import numpy as np

PHASE_NS_GREEN  = 0  # ACTION 0: verde Norte-Sul
PHASE_NS_YELLOW = 1  # amarelo NS
PHASE_NS_RED    = 2  # tudo vermelho apos NS
PHASE_EW_GREEN  = 3  # ACTION 1: verde Este-Oeste
PHASE_EW_YELLOW = 4  # amarelo EW
PHASE_EW_RED    = 5  # tudo vermelho apos EW

NUM_ACTIONS = 2
MAX_EDGES   = 4   # todas as routes têm 4 edges
# num_states = 164 (base) + 2 (action_encode) + 4 (lane_occupancy) = 170


class Intersection:
    def __init__(self, id, num_states):
        self.id = id
        self.dur = -1
        self.action = -1
        self.yellow = 0
        self.green_duration = 10
        self.yellow_duration = 4
        self.num_states = num_states

        # training
        self.reward_episode = []
        self.cumulative_wait = []
        self.sum_neg_reward = 0
        self.wait_veh = 0
        self.wait_ped = 0
        self.old_state = None
        self.old_action = -1
        self.old_total_wait = 0
        self.old_ped_wait = 0

        # testing
        self.queue_length = []
        self.phase_activated = []
        self.awt_greenArea = []
        self.waitingVeh = []
        self.avgspeed_greenArea = []
        self.avgspeed = []
        self.pedestrians_halting = []
        self.phase_duration = [0] * NUM_ACTIONS
        self.n_times_active = [0] * NUM_ACTIONS
        self.phase_extension_1_hour = [0] * (NUM_ACTIONS + 1)
        self.phase_extension_5min = [0] * (NUM_ACTIONS + 1)
        self.phase_durations = [[] for _ in range(NUM_ACTIONS + 1)]

    def collect_waiting_times(self, roads):
        return sum(traci.edge.getWaitingTime(e) for e in roads)

    def pedestrians_WaitingTime(self, wz):
        total = 0
        for area in wz[0]:
            for ped in traci.edge.getLastStepPersonIDs(area):
                total += traci.person.getWaitingTime(ped)
        return total

    def _get_lane_ids(self, edge_id):
        try:
            n = traci.edge.getLaneNumber(edge_id)
            return [f"{edge_id}_{i}" for i in range(n)]
        except Exception:
            return [f"{edge_id}_0"]

    def lane_occupancy(self, state, routes):
        """Adiciona MAX_EDGES valores de ocupacao ao estado (padding com 0 se route < MAX_EDGES)."""
        occupancy_array = np.zeros(MAX_EDGES)
        for i, edge_id in enumerate(routes):
            if i >= MAX_EDGES:
                break
            lane_ids = self._get_lane_ids(edge_id)
            occupancy_array[i] = np.mean([traci.lane.getLastStepOccupancy(lid) for lid in lane_ids])
        return np.concatenate([state, occupancy_array])

    def choose_phase(self, step, action, old_action, name, yellow, idx, routes, map_env, sapa):
        if step != 0 and old_action != action and old_action != -1 and yellow == 0:
            self.set_yellow_phase(old_action, name)
            return self.yellow_duration, 1
        else:
            self.set_green_phase(action, name)
           #dur = sapa.sapa_block(idx, routes, map_env, action)
            return self.green_duration, 0

    def set_green_phase(self, action_number, TL_NAME):
        if action_number == 0:
            traci.trafficlight.setPhase(TL_NAME, PHASE_NS_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase(TL_NAME, PHASE_EW_GREEN)

    def set_yellow_phase(self, old_action, TL_NAME):
        if old_action == 0:
            traci.trafficlight.setPhase(TL_NAME, PHASE_NS_YELLOW)
        elif old_action == 1:
            traci.trafficlight.setPhase(TL_NAME, PHASE_EW_YELLOW)

    def pedestrians_state(self, state, wz):
        for area in wz[0]:
            for ped in traci.edge.getLastStepPersonIDs(area):
                lid = traci.person.getLaneID(ped)
                spd = traci.person.getSpeed(ped)
                for i, wl in enumerate(wz[1][:4]):
                    if lid == wl and spd < 0.1:
                        state[80 + i] = 1
        return state

    def get_cell(self, pos, thresholds):
        for i, th in enumerate(thresholds):
            if pos < th:
                return i
        return len(thresholds) - 1

    def lane_group(self, route, edge_id):
        try:
            pos = list(route).index(edge_id)
        except ValueError:
            return -1

        # Convenção canónica de entrada:
        # - 4 entradas: [N, O, S, E]
        # - 6 entradas: [N1, N2, O, S1, S2, E]
        # O mapeamento mantém os mesmos grupos cardinais no estado.
        if len(route) == 6:
            return {0: 2, 1: 2, 2: 0, 3: 6, 4: 6, 5: 4}.get(pos, -1)

        return {0: 2, 1: 0, 2: 6, 3: 4}.get(pos, -1)

    def action_encode(self, state, action):
        phases = [0] * NUM_ACTIONS
        if 0 <= action < NUM_ACTIONS:
            phases[action] = 1
        return np.concatenate([state, phases])

    def get_state(self, idx, wz, routes, lanes_200_400, action):
        thresholds_200 = [7, 15, 25, 35, 55, 70, 100, 130, 150, 200]
        thresholds_400 = [7, 15, 25, 35, 55, 75, 100, 150, 200, 400]
        thresholds_100 = [7, 14, 20, 30, 40, 50, 60, 70, 80, 100]

        num_states_base = 164
        state = np.zeros(num_states_base)

        lane = routes[idx]
        lanes200 = lanes_200_400[0]
        lanes400 = lanes_200_400[1]

        for edge_id in lane:
            if edge_id in lanes200:
                thresholds, lane_len = thresholds_200, 200
            elif edge_id in lanes400:
                thresholds, lane_len = thresholds_400, 400
            else:
                thresholds, lane_len = thresholds_100, 100

            lg = self.lane_group(lane, edge_id)
            if lg == -1:
                continue

            for lid in self._get_lane_ids(edge_id):
                try:
                    cars = traci.lane.getLastStepVehicleIDs(lid)
                except Exception:
                    continue
                for car_id in cars:
                    pos = lane_len - traci.vehicle.getLanePosition(car_id)
                    cell = self.get_cell(pos, thresholds)
                    ci = lg * 10 + cell
                    si = 84 + ci
                    if ci < num_states_base:
                        state[ci] = 1
                    if si < num_states_base:
                        v = traci.vehicle.getSpeed(car_id)
                        state[si] = (state[si] + v / 13.89) / 2

        state = self.pedestrians_state(state, wz)
        state = self.action_encode(state, action)   # +2  -> 166
        state = self.lane_occupancy(state, lane)    # +6  -> 172

        return state