import traci
import numpy as np

PHASE_NS_GREEN  = 0  # verde Norte-Sul
PHASE_NS_YELLOW = 1  # amarelo NS
PHASE_NS_RED    = 2  # tudo vermelho após NS
PHASE_EW_GREEN  = 3  # verde Este-Oeste
PHASE_EW_YELLOW = 4  # amarelo EW
PHASE_EW_RED    = 5  # tudo vermelho após EW

NUM_ACTIONS_PHASE    = 2               # fases possíveis: NS ou EW
NUM_ACTIONS_DURATION = 4               # durações possíveis: 10, 20, 30, 40s
DURATION_VALUES      = [10, 20, 30, 40]  # segundos de verde

# ── Ação combinada (fase + duração) ─────────────────────────────────────────
# Ação 0 → NS + 10s  |  Ação 4 → EW + 10s
# Ação 1 → NS + 20s  |  Ação 5 → EW + 20s
# Ação 2 → NS + 30s  |  Ação 6 → EW + 30s
# Ação 3 → NS + 40s  |  Ação 7 → EW + 40s
NUM_ACTIONS_COMBINED = NUM_ACTIONS_PHASE * NUM_ACTIONS_DURATION  # 8

NUM_ACTIONS = NUM_ACTIONS_COMBINED   # alias usado pelo caller
MAX_EDGES   = 4

INTERSECTIONS_PER_LANE = {2, 4}   # J2 e J4 têm edges com 3 lanes

# ── Thresholds de distância (10 células por grupo) ──────────────────────────
_THRESH_200 = [7, 15, 25, 35, 55, 70, 100, 130, 150, 200]
_THRESH_400 = [7, 15, 25, 35, 55, 75, 100, 150, 200, 400]
_THRESH_100 = [7, 14, 20, 30, 40, 50, 60,  70,  80,  100]


def decode_action(action):
    """
    Converte a ação combinada (0-7) em (phase, green_duration).

    phase          = action // NUM_ACTIONS_DURATION   (0=NS, 1=EW)
    green_duration = DURATION_VALUES[action % NUM_ACTIONS_DURATION]

    Exemplos:
      decode_action(0) → (0, 10)   NS + 10s
      decode_action(3) → (0, 40)   NS + 40s
      decode_action(4) → (1, 10)   EW + 10s
      decode_action(7) → (1, 40)   EW + 40s
    """
    phase    = action // NUM_ACTIONS_DURATION
    duration = DURATION_VALUES[action % NUM_ACTIONS_DURATION]
    return phase, duration


class Intersection:
    def __init__(self, id, num_states):
        self.id          = id
        self.dur         = -1
        self.action      = -1       # ação COMBINADA (0-7): fase + duração
        self.yellow          = 0
        self.yellow_duration = 4
        self.num_states      = num_states

        # training
        self.reward_episode  = []
        self.cumulative_wait = []
        self.sum_neg_reward  = 0
        self.wait_veh = 0
        self.wait_ped = 0
        self.old_state      = None
        self.old_action     = -1
        self.old_total_wait = 0
        self.old_ped_wait   = 0

        # testing — indexados por FASE (0=NS, 1=EW) para manter compatibilidade
        self.queue_length         = []
        self.phase_activated      = []
        self.awt_greenArea        = []
        self.waitingVeh           = []
        self.avgspeed_greenArea   = []
        self.avgspeed             = []
        self.pedestrians_halting  = []
        self.phase_duration       = [0] * NUM_ACTIONS_PHASE
        self.n_times_active       = [0] * NUM_ACTIONS_PHASE
        self.phase_extension_1_hour = [0] * (NUM_ACTIONS_PHASE + 1)
        self.phase_extension_5min   = [0] * (NUM_ACTIONS_PHASE + 1)
        self.phase_durations        = [[] for _ in range(NUM_ACTIONS_PHASE + 1)]
        self.duration_log           = {0: [], 1: []}  # durações escolhidas por fase

    # ── Esperas ─────────────────────────────────────────────────────────────

    def collect_waiting_times(self, roads):
        return sum(traci.edge.getWaitingTime(e) for e in roads)

    def pedestrians_WaitingTime(self, wz):
        total = 0
        for area in wz[0]:
            for ped in traci.edge.getLastStepPersonIDs(area):
                total += traci.person.getWaitingTime(ped)
        return total

    # ── Auxiliares ──────────────────────────────────────────────────────────

    def _get_lane_ids(self, edge_id):
        try:
            n = traci.edge.getLaneNumber(edge_id)
            return [f"{edge_id}_{i}" for i in range(n)]
        except Exception:
            return [f"{edge_id}_0"]

    def _get_thresholds(self, edge_id, lanes200, lanes400):
        if edge_id in lanes200:
            return _THRESH_200, 200
        elif edge_id in lanes400:
            return _THRESH_400, 400
        else:
            return _THRESH_100, 100

    def get_cell(self, pos, thresholds):
        for i, th in enumerate(thresholds):
            if pos < th:
                return i
        return len(thresholds) - 1

    def lane_group(self, route, edge_id):
        """Mantido para compatibilidade — não usado pelo novo get_state."""
        try:
            pos = list(route).index(edge_id)
        except ValueError:
            return -1
        if len(route) == 6:
            return {0: 2, 1: 2, 2: 0, 3: 6, 4: 6, 5: 4}.get(pos, -1)
        return {0: 2, 1: 0, 2: 6, 3: 4}.get(pos, -1)

    # ── Lógica de fases ─────────────────────────────────────────────────────

    def choose_phase(self, step, phase, old_phase, name, yellow):
        """
        Recebe a FASE decodificada (0=NS ou 1=EW), não a ação combinada.
        A duração já foi extraída por decode_action() no caller.
        """
        if step != 0 and old_phase != phase and old_phase != -1 and yellow == 0:
            self.set_yellow_phase(old_phase, name)
            return self.yellow_duration, 1
        else:
            self.set_green_phase(phase, name)
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

    # ── Métodos antigos — COMENTADOS ────────────────────────────────────────

    # def lane_occupancy(self, state, routes): ...
    # def lane_occupancy_per_lane(self, state, routes): ...
    # def pedestrians_state(self, state, wz): ...
    # def action_encode(self, state, action): ...
    # def _build_base_state(self, idx, wz, routes, lanes_200_400, action): ...
    # def get_state_OLD(self, idx, wz, routes, lanes_200_400, action): ...
    # def get_state_duration(self, idx, wz, routes, lanes_200_400, action): ...

    # ── get_state ────────────────────────────────────────────────────────────

    def get_state(self, idx, wz, routes, lanes_200_400, action):
        """
        Constrói o estado para as redes de fase+duração combinadas.
        O parâmetro `action` é aceite por compatibilidade mas não é usado.

        Cell_1 (idx=1 ou 3) — 84 estados:
          índices   0-39  → presença   (4 abordagens × 10 células)
          índices  40-79  → speed      (4 abordagens × 10 células)
          índices  80-83  → peões      (4 zonas)

        Cell_2 (idx=2 ou 4) — 124 estados:
          Edge 510_NS_1 (3 lanes): lanes 0+1 → grupo 0 | lane 2 → grupo 1
          Edge EG_WE_2  (2 lanes): lanes 0+1 → grupo 2
          Edge 510_SN_2 (3 lanes): lanes 0+1 → grupo 3 | lane 2 → grupo 4
          Edge EG_EW_1  (2 lanes): lanes 0+1 → grupo 5
          índices   0-59  → presença   (6 grupos × 10 células)
          índices  60-119 → speed      (6 grupos × 10 células)
          índices 120-123 → peões      (4 zonas)
        """
        lanes200, lanes400 = lanes_200_400[0], lanes_200_400[1]
        lane = routes[idx]

        if idx in (1, 3):
            # ── Cell_1 ───────────────────────────────────────────────
            n_presence = 40
            ped_offset = 80
            state      = np.zeros(84)

            for approach_idx, edge_id in enumerate(lane[:4]):
                thresholds, lane_len = self._get_thresholds(edge_id, lanes200, lanes400)
                for lid in self._get_lane_ids(edge_id):
                    try:
                        cars = traci.lane.getLastStepVehicleIDs(lid)
                    except Exception:
                        continue
                    for car_id in cars:
                        pos  = lane_len - traci.vehicle.getLanePosition(car_id)
                        cell = self.get_cell(pos, thresholds)
                        ci   = approach_idx * 10 + cell
                        state[ci] = 1
                        v  = traci.vehicle.getSpeed(car_id)
                        si = n_presence + ci
                        state[si] = (state[si] + v / 13.89) / 2

        else:
            # ── Cell_2 ───────────────────────────────────────────────
            n_presence = 60
            ped_offset = 120
            state      = np.zeros(124)

            group_idx = 0
            for edge_id in lane[:MAX_EDGES]:
                if group_idx >= 6:
                    break
                thresholds, lane_len = self._get_thresholds(edge_id, lanes200, lanes400)
                lane_ids = self._get_lane_ids(edge_id)
                n_lanes  = len(lane_ids)

                if n_lanes >= 3:
                    for lid_pos, lid in enumerate(lane_ids):
                        g = group_idx if lid_pos < n_lanes - 1 else group_idx + 1
                        try:
                            cars = traci.lane.getLastStepVehicleIDs(lid)
                        except Exception:
                            continue
                        for car_id in cars:
                            pos  = lane_len - traci.vehicle.getLanePosition(car_id)
                            cell = self.get_cell(pos, thresholds)
                            ci   = g * 10 + cell
                            state[ci] = 1
                            v  = traci.vehicle.getSpeed(car_id)
                            si = n_presence + ci
                            state[si] = (state[si] + v / 13.89) / 2
                    group_idx += 2
                else:
                    for lid in lane_ids:
                        try:
                            cars = traci.lane.getLastStepVehicleIDs(lid)
                        except Exception:
                            continue
                        for car_id in cars:
                            pos  = lane_len - traci.vehicle.getLanePosition(car_id)
                            cell = self.get_cell(pos, thresholds)
                            ci   = group_idx * 10 + cell
                            state[ci] = 1
                            v  = traci.vehicle.getSpeed(car_id)
                            si = n_presence + ci
                            state[si] = (state[si] + v / 13.89) / 2
                    group_idx += 1

        # ── Peões ────────────────────────────────────────────────────
        for area in wz[0]:
            for ped in traci.edge.getLastStepPersonIDs(area):
                lid_p = traci.person.getLaneID(ped)
                spd   = traci.person.getSpeed(ped)
                for i, wl in enumerate(wz[1][:4]):
                    if lid_p == wl and spd < 0.1:
                        state[ped_offset + i] = 1

        return state