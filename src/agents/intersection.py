import traci
import numpy as np

PHASE_NS_GREEN  = 0  # ACTION 0: verde Norte-Sul
PHASE_NS_YELLOW = 1  # amarelo NS
PHASE_NS_RED    = 2  # tudo vermelho apos NS
PHASE_EW_GREEN  = 3  # ACTION 1: verde Este-Oeste
PHASE_EW_YELLOW = 4  # amarelo EW
PHASE_EW_RED    = 5  # tudo vermelho apos EW

# Redes de fase: 2 ações (NS ou EW)
NUM_ACTIONS_PHASE    = 2
# Rede de duração: 4 ações (8s, 16s, 24s, 32s)
NUM_ACTIONS_DURATION = 4
DURATION_VALUES      = [8, 16, 24, 32]

NUM_ACTIONS = NUM_ACTIONS_PHASE   # mantido para compatibilidade com action_encode (usa NUM_ACTIONS_PHASE)
MAX_EDGES   = 4                   # todas as routes têm 4 edges

# num_states Cell_1 (C1/C3): 164 (base) + 2 (action_encode) + 4  (lane_occupancy média)     = 170
# num_states Cell_2 (C2/C4): 164 (base) + 2 (action_encode) + 10 (lane_occupancy por lane)  = 176
# num_states Cell_Duration:  170 (igual a Cell_1, mesma dimensão para todos os cruzamentos)

# cruzamentos que usam lane_occupancy por lane (têm edges com 3 lanes)
INTERSECTIONS_PER_LANE = {2, 4}  # J2 e J4 — edges 510_* têm 3 lanes


class Intersection:
    def __init__(self, id, num_states):
        self.id = id
        self.dur = -1
        self.action = -1          # ação de FASE (0=NS, 1=EW)
        self.action_dur = -1      # ação de DURAÇÃO (0-3 → 8,16,24,32s)
        self.yellow = 0
        self.yellow_duration = 4
        self.num_states = num_states

        # training
        self.reward_episode = []
        self.cumulative_wait = []
        self.sum_neg_reward = 0
        self.wait_veh = 0
        self.wait_ped = 0
        self.old_state = None
        self.old_duration_state = None  # ADICIONADO: estado 170-dim para Cell_Duration
        self.old_action = -1            # fase anterior
        self.old_action_dur = -1        # duração anterior
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
        self.phase_duration = [0] * NUM_ACTIONS_PHASE
        self.n_times_active = [0] * NUM_ACTIONS_PHASE
        self.phase_extension_1_hour = [0] * (NUM_ACTIONS_PHASE + 1)
        self.phase_extension_5min   = [0] * (NUM_ACTIONS_PHASE + 1)
        self.phase_durations        = [[] for _ in range(NUM_ACTIONS_PHASE + 1)]

        # testing - durações escolhidas pela rede de duração por fase
        self.duration_log = {0: [], 1: []}   # fase 0 (NS) e fase 1 (EW)

    # ------------------------------------------------------------------
    # Coleta de esperas
    # ------------------------------------------------------------------

    def collect_waiting_times(self, roads):
        return sum(traci.edge.getWaitingTime(e) for e in roads)

    def pedestrians_WaitingTime(self, wz):
        total = 0
        for area in wz[0]:
            for ped in traci.edge.getLastStepPersonIDs(area):
                total += traci.person.getWaitingTime(ped)
        return total

    # ------------------------------------------------------------------
    # Auxiliares de lane
    # ------------------------------------------------------------------

    def _get_lane_ids(self, edge_id):
        try:
            n = traci.edge.getLaneNumber(edge_id)
            return [f"{edge_id}_{i}" for i in range(n)]
        except Exception:
            return [f"{edge_id}_0"]

    # ------------------------------------------------------------------
    # Ocupação de faixas
    # ------------------------------------------------------------------

    def lane_occupancy(self, state, routes):
        """
        C1/C3: adiciona 4 valores de ocupação (média por edge) → +4 dims.
        Também usado pela Cell_Duration para todos os cruzamentos (dimensão fixa).
        """
        occupancy_array = np.zeros(MAX_EDGES)
        for i, edge_id in enumerate(routes):
            if i >= MAX_EDGES:
                break
            lane_ids = self._get_lane_ids(edge_id)
            occupancy_array[i] = np.mean([traci.lane.getLastStepOccupancy(lid) for lid in lane_ids])
        return np.concatenate([state, occupancy_array])

    def lane_occupancy_per_lane(self, state, routes):
        """
        C2/C4: adiciona ocupação por lane individual → +10 dims.
        510_NS_1: 3 + EG_WE_2: 2 + 510_SN_2: 3 + EG_EW_1: 2 = 10 valores
        """
        occupancy_list = []
        for edge_id in routes[:MAX_EDGES]:
            lane_ids = self._get_lane_ids(edge_id)
            for lid in lane_ids:
                occupancy_list.append(traci.lane.getLastStepOccupancy(lid))
        return np.concatenate([state, np.array(occupancy_list)])

    # ------------------------------------------------------------------
    # Lógica de fases
    # ------------------------------------------------------------------

    def choose_phase(self, step, action, old_action, name, yellow):
        """
        Decide se aplica amarelo (transição) ou verde.
        Recebe a FASE (action: 0=NS, 1=EW) e a duração já calculada externamente.
        Retorna (dur, yellow_flag) — a duração é gerida pelo caller.
        """
        if step != 0 and old_action != action and old_action != -1 and yellow == 0:
            self.set_yellow_phase(old_action, name)
            return self.yellow_duration, 1
        else:
            self.set_green_phase(action, name)
            return 0, 0

    def set_green_phase(self, phase_id, TL_NAME):
        if phase_id == 0:
            traci.trafficlight.setPhase(TL_NAME, PHASE_NS_GREEN)
        elif phase_id == 1:
            traci.trafficlight.setPhase(TL_NAME, PHASE_EW_GREEN)

    def set_yellow_phase(self, phase_id, TL_NAME):
        if phase_id == 0:
            traci.trafficlight.setPhase(TL_NAME, PHASE_NS_YELLOW)
        elif phase_id == 1:
            traci.trafficlight.setPhase(TL_NAME, PHASE_EW_YELLOW)

    # ------------------------------------------------------------------
    # Construção do estado
    # ------------------------------------------------------------------

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

        if len(route) == 6:
            return {0: 2, 1: 2, 2: 0, 3: 6, 4: 6, 5: 4}.get(pos, -1)

        return {0: 2, 1: 0, 2: 6, 3: 4}.get(pos, -1)

    def action_encode(self, state, action):
        """Codifica a FASE (0 ou 1) em one-hot de 2 dims."""
        phases = [0] * NUM_ACTIONS_PHASE
        if 0 <= action < NUM_ACTIONS_PHASE:
            phases[action] = 1
        return np.concatenate([state, phases])

    def _build_base_state(self, idx, wz, routes, lanes_200_400, action):
        """Constrói os 166 dims base (164 + 2 action_encode) comuns a todos os métodos."""
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
        state = self.action_encode(state, action)  # +2 → 166
        return state, lane

    def get_state(self, idx, wz, routes, lanes_200_400, action):
        """
        Estado para redes de fase:
          C1/C3 (idx=1,3): 166 + 4  = 170  (lane_occupancy média)
          C2/C4 (idx=2,4): 166 + 10 = 176  (lane_occupancy por lane)
        """
        state, lane = self._build_base_state(idx, wz, routes, lanes_200_400, action)

        if idx in INTERSECTIONS_PER_LANE:
            return self.lane_occupancy_per_lane(state, lane)  # → 176
        else:
            return self.lane_occupancy(state, lane)            # → 170

    def get_state_duration(self, idx, wz, routes, lanes_200_400, action):
        """
        Estado para Cell_Duration: sempre 170 dims para todos os cruzamentos.
        Usa lane_occupancy com média independentemente do cruzamento,
        conforme pedido pelo professor ("mesma dimensão para todos").
        """
        state, lane = self._build_base_state(idx, wz, routes, lanes_200_400, action)
        return self.lane_occupancy(state, lane)  # → 170 para todos