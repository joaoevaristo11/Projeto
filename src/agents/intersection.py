import traci
import numpy as np

PHASE_NS_GREEN  = 0  # ACTION 0: verde Norte-Sul
PHASE_NS_YELLOW = 1  # amarelo NS
PHASE_NS_RED    = 2  # tudo vermelho após NS
PHASE_EW_GREEN  = 3  # ACTION 1: verde Este-Oeste
PHASE_EW_YELLOW = 4  # amarelo EW
PHASE_EW_RED    = 5  # tudo vermelho após EW

NUM_ACTIONS_PHASE    = 2
NUM_ACTIONS_DURATION = 4           # mantido para compatibilidade
DURATION_VALUES      = [8, 16, 24, 32]  # mantido para compatibilidade

NUM_ACTIONS = NUM_ACTIONS_PHASE
MAX_EDGES   = 4

INTERSECTIONS_PER_LANE = {2, 4}   # J2 e J4 têm edges com 3 lanes

# ── Thresholds de distância (10 células por grupo) ──────────────────────────
_THRESH_200 = [7, 15, 25, 35, 55, 70, 100, 130, 150, 200]
_THRESH_400 = [7, 15, 25, 35, 55, 75, 100, 150, 200, 400]
_THRESH_100 = [7, 14, 20, 30, 40, 50, 60,  70,  80,  100]


class Intersection:
    def __init__(self, id, num_states):
        self.id          = id
        self.dur         = -1
        self.action      = -1       # ação de FASE (0=NS, 1=EW)
        self.action_dur  = -1       # mantido para compatibilidade
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
        # self.old_duration_state = None  # DESATIVADO: Cell_Duration comentada
        self.old_action     = -1
        self.old_action_dur = -1    # mantido para compatibilidade
        self.old_total_wait = 0
        self.old_ped_wait   = 0

        # testing
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
        self.duration_log           = {0: [], 1: []}

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

    def choose_phase(self, step, action, old_action, name, yellow):
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

    # ── Métodos antigos — COMENTADOS ────────────────────────────────────────
    # Para reverter à arquitetura anterior (170/176 dims + action_encode):
    # descomentar tudo abaixo e repor get_state_OLD como get_state.

    # def lane_occupancy(self, state, routes):
    #     """C1/C3: +4 dims de ocupação média por edge."""
    #     occupancy_array = np.zeros(MAX_EDGES)
    #     for i, edge_id in enumerate(routes):
    #         if i >= MAX_EDGES:
    #             break
    #         lane_ids = self._get_lane_ids(edge_id)
    #         occupancy_array[i] = np.mean(
    #             [traci.lane.getLastStepOccupancy(lid) for lid in lane_ids]
    #         )
    #     return np.concatenate([state, occupancy_array])

    # def lane_occupancy_per_lane(self, state, routes):
    #     """C2/C4: +10 dims de ocupação por lane individual.
    #     510_NS_1: 3 + EG_WE_2: 2 + 510_SN_2: 3 + EG_EW_1: 2 = 10 valores."""
    #     occupancy_list = []
    #     for edge_id in routes[:MAX_EDGES]:
    #         for lid in self._get_lane_ids(edge_id):
    #             occupancy_list.append(traci.lane.getLastStepOccupancy(lid))
    #     return np.concatenate([state, np.array(occupancy_list)])

    # def pedestrians_state(self, state, wz):
    #     """DESATIVADO: índice 80 era fixo — errado para Cell_2 (offset 120).
    #     Lógica de peões integrada diretamente no novo get_state."""
    #     for area in wz[0]:
    #         for ped in traci.edge.getLastStepPersonIDs(area):
    #             lid = traci.person.getLaneID(ped)
    #             spd = traci.person.getSpeed(ped)
    #             for i, wl in enumerate(wz[1][:4]):
    #                 if lid == wl and spd < 0.1:
    #                     state[80 + i] = 1
    #     return state

    # def action_encode(self, state, action):
    #     """DESATIVADO: removido por indicação do professor."""
    #     phases = [0] * NUM_ACTIONS_PHASE
    #     if 0 <= action < NUM_ACTIONS_PHASE:
    #         phases[action] = 1
    #     return np.concatenate([state, phases])

    # def _build_base_state(self, idx, wz, routes, lanes_200_400, action):
    #     """DESATIVADO: construía 164 dims + 2 action_encode = 166 dims.
    #     Substituído pelo novo get_state."""
    #     thresholds_200 = [7, 15, 25, 35, 55, 70, 100, 130, 150, 200]
    #     thresholds_400 = [7, 15, 25, 35, 55, 75, 100, 150, 200, 400]
    #     thresholds_100 = [7, 14, 20, 30, 40, 50, 60, 70, 80, 100]
    #     num_states_base = 164
    #     state = np.zeros(num_states_base)
    #     lane = routes[idx]
    #     lanes200, lanes400 = lanes_200_400[0], lanes_200_400[1]
    #     for edge_id in lane:
    #         if edge_id in lanes200:
    #             thresholds, lane_len = thresholds_200, 200
    #         elif edge_id in lanes400:
    #             thresholds, lane_len = thresholds_400, 400
    #         else:
    #             thresholds, lane_len = thresholds_100, 100
    #         lg = self.lane_group(lane, edge_id)
    #         if lg == -1:
    #             continue
    #         for lid in self._get_lane_ids(edge_id):
    #             try:
    #                 cars = traci.lane.getLastStepVehicleIDs(lid)
    #             except Exception:
    #                 continue
    #             for car_id in cars:
    #                 pos = lane_len - traci.vehicle.getLanePosition(car_id)
    #                 cell = self.get_cell(pos, thresholds)
    #                 ci = lg * 10 + cell
    #                 si = 84 + ci
    #                 if ci < num_states_base:
    #                     state[ci] = 1
    #                 if si < num_states_base:
    #                     v = traci.vehicle.getSpeed(car_id)
    #                     state[si] = (state[si] + v / 13.89) / 2
    #     state = self.pedestrians_state(state, wz)
    #     state = self.action_encode(state, action)  # +2 → 166
    #     return state, lane

    # def get_state_OLD(self, idx, wz, routes, lanes_200_400, action):
    #     """DESATIVADO — estado anterior 170/176 dims.
    #     C1/C3: 166 + 4  = 170  (lane_occupancy média)
    #     C2/C4: 166 + 10 = 176  (lane_occupancy por lane)"""
    #     state, lane = self._build_base_state(idx, wz, routes, lanes_200_400, action)
    #     if idx in INTERSECTIONS_PER_LANE:
    #         return self.lane_occupancy_per_lane(state, lane)  # → 176
    #     else:
    #         return self.lane_occupancy(state, lane)            # → 170

    # ── get_state — NOVA VERSÃO ──────────────────────────────────────────────

    def get_state(self, idx, wz, routes, lanes_200_400, action):
        """
        Constrói o estado para as redes de fase.
        Sem action_encode. Sem lane_occupancy. Indexação densa.
        O parâmetro `action` é aceite por compatibilidade mas não é usado.

        ── Cell_1 (idx=1 ou 3) — 84 estados ───────────────────────────────
          4 abordagens (edges), 1 grupo por edge, 10 células por grupo:
            índices   0-39  → presença de veículos
            índices  40-79  → velocidade média normalizada
            índices  80-83  → peões parados (1 bit por zona)

        ── Cell_2 (idx=2 ou 4) — 124 estados ──────────────────────────────
          4 edges com estrutura de lanes variável → 6 grupos, 10 células cada:
            Edge 510_NS_1 (3 lanes): lanes 0+1 → grupo 0 | lane 2 → grupo 1
            Edge EG_WE_2  (2 lanes): lanes 0+1 → grupo 2
            Edge 510_SN_2 (3 lanes): lanes 0+1 → grupo 3 | lane 2 → grupo 4
            Edge EG_EW_1  (2 lanes): lanes 0+1 → grupo 5
            índices   0-59  → presença de veículos  (6 grupos × 10 células)
            índices  60-119 → velocidade média       (6 grupos × 10 células)
            índices 120-123 → peões parados          (4 zonas)
        """
        lanes200, lanes400 = lanes_200_400[0], lanes_200_400[1]
        lane = routes[idx]

        if idx in (1, 3):
            # ── Cell_1: 4 abordagens, 1 grupo por edge ───────────────
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
                        ci   = approach_idx * 10 + cell        # presença: 0..39
                        state[ci] = 1
                        v  = traci.vehicle.getSpeed(car_id)
                        si = n_presence + ci                   # speed: 40..79
                        state[si] = (state[si] + v / 13.89) / 2

        else:
            # ── Cell_2: 4 edges, 6 grupos no total ───────────────────
            # Edges com 3 lanes: lanes[:-1] → grupo N, lane[-1] → grupo N+1
            # Edges com 2 lanes: todas as lanes  → grupo N
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
                    # lanes 0..n-2 → group_idx  |  lane n-1 → group_idx+1
                    for lid_pos, lid in enumerate(lane_ids):
                        g = group_idx if lid_pos < n_lanes - 1 else group_idx + 1
                        try:
                            cars = traci.lane.getLastStepVehicleIDs(lid)
                        except Exception:
                            continue
                        for car_id in cars:
                            pos  = lane_len - traci.vehicle.getLanePosition(car_id)
                            cell = self.get_cell(pos, thresholds)
                            ci   = g * 10 + cell               # presença: 0..59
                            state[ci] = 1
                            v  = traci.vehicle.getSpeed(car_id)
                            si = n_presence + ci               # speed: 60..119
                            state[si] = (state[si] + v / 13.89) / 2
                    group_idx += 2
                else:
                    # 1 ou 2 lanes → todas no mesmo grupo
                    for lid in lane_ids:
                        try:
                            cars = traci.lane.getLastStepVehicleIDs(lid)
                        except Exception:
                            continue
                        for car_id in cars:
                            pos  = lane_len - traci.vehicle.getLanePosition(car_id)
                            cell = self.get_cell(pos, thresholds)
                            ci   = group_idx * 10 + cell       # presença: 0..59
                            state[ci] = 1
                            v  = traci.vehicle.getSpeed(car_id)
                            si = n_presence + ci               # speed: 60..119
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

    # ── get_state_duration — DESATIVADO ─────────────────────────────────────

    # def get_state_duration(self, idx, wz, routes, lanes_200_400, action):
    #     """
    #     DESATIVADO: estado para Cell_Duration (sempre 170 dims).
    #     Temporariamente comentado — rede de duração fora de uso.
    #     Para reativar: descomentar _build_base_state e lane_occupancy acima.
    #     """
    #     state, lane = self._build_base_state(idx, wz, routes, lanes_200_400, action)
    #     return self.lane_occupancy(state, lane)  # → 170 para todos