import traci
import numpy as np

PHASE_NS_FD = 0  #ACTION 1
PHASE_NS_YELLOW = 1
PHASE_N_ALL = 2  #ACTION 2
PHASE_N_ALL_YELLOW = 3
PHASE_S_ALL = 4  #ACTION 3
PHASE_S_ALL_YELLOW = 5
PHASE_NS_LEFT = 6  #ACTION 4
PHASE_NS_LEFT_YELLOW = 7
PHASE_WE_FD = 8  #ACTION 5
PHASE_WE_FD_YELLOW = 9
PHASE_W_ALL = 10  #ACTION 6
PHASE_W_ALL_YELLOW = 11
PHASE_E_ALL = 12  #ACTION 7
PHASE_E_ALL_YELLOW = 13
PHASE_WE_LEFT = 14  #ACTION 8
PHASE_WE_LEFT_YELLOW = 15

PEDESTRIAN_PHASE = 32
ALL_RED_PHASE = 33

class Intersection:
    def __init__(self, id, num_states):
        """Inicia cada interseção com o seu id."""
        self.id = id

        #variaveis comuns aos cruzamentos
        self.dur = -1
        self.action = -1
        self.yellow = 0
        self.green_duration = 8 #base duration
        self.yellow_duration = 4 #base yellow duration
        self.num_states = num_states

        #training variables
        self.reward_episode = []
        self.cumulative_wait = []
        self.sum_neg_reward = 0
        self.wait_veh = 0
        self.wait_ped = 0

        #old state metrics
        self.old_state = None
        self.old_action = -1
        self.old_total_wait = 0
        self.old_ped_wait = 0

        #testing network metrics
        self.queue_length = []
        self.phase_activated = []
        self.awt_greenArea = [] #for critical intersections C1 / C5 / C2 armazena valores médios por minuto
        self.waitingVeh = [] #variavel auxiliar para contar que armazena valoresmédios a cada segundo
        self.avgspeed_greenArea = [] #armazena valores médios por minuto
        self.avgspeed = [] #armazena valores médios por segundo
        self.pedestrians_halting = []
        self.phase_duration = [0] * 9 #marca o tempo inicial da fase
        self.n_times_active = [0] * 9  # variavies para ver a duração de fase e as vezes que sao ativas para média
        self.phase_extension_1_hour = [0] * 10
        self.phase_extension_5min = [0] * 13
        self.phase_durations = [[] for _ in range(10)]


    def cumulative_negative_reward(self, reward):
        """Adicionar recompensa ao cruzamento."""
        self.sum_reward += reward


    def episode_reward(self, reward):
        """Guarda o reward final de cada episódio"""
        self.reward_episode.append(reward)


    def set_duration(self, dur):
        """Define duração da fase."""
        self.dur = dur


    def phasetime_simulation(self):
        self.dur = self.dur - 1


    def collect_waiting_times(self, roads):
        """
        Retrieve the waiting time of every car in the incoming roads
        """
        total_waiting_time = 0

        for edge in roads:
            total_waiting_time += traci.edge.getWaitingTime(edge)

        return total_waiting_time


    def pedestrians_WaitingTime(self, wz):
        """
        Retrieve the waiting time of every pedestrian in the waiting zones
        """
        total_waiting_times_ped = 0
        for waiting_areas in wz[0]:
            ped_list = traci.edge.getLastStepPersonIDs(waiting_areas)
            for ped in ped_list:
                wait_time = traci.person.getWaitingTime(ped)
                total_waiting_times_ped += wait_time
        return total_waiting_times_ped
    
    def lane_occupancy(self, state, routes):
        """
        Retrieve the occupancy of each incoming lane for state observation
        """

        occupancy_array = []

        # 2. Percorrer a tua lista de 8 estradas
        for lane_id in routes:
            valor = traci.lane.getLastStepOccupancy(lane_id)
            occupancy_array.append(valor)

        new_state = np.concatenate([state, occupancy_array])

        return new_state


    def choose_phase(self, step, action, old_action, name, yellow, idx, routes, map_env, sapa):
        """Chooses another action to activate or maintain the same. If it activates different phases first come a yellow phase, then the green phase of new action.
        The phase time is given by SAPA block"""

        # if the chosen phase is different from the last phase, activate the yellow phase
        if step != 0 and old_action != action and old_action != -1 and yellow == 0:

            #Pedestrian phase
            if old_action == 8:
                self.set_yellow_phase(old_action, name)
                dur = self.green_duration  #12 segundos de verde e 8 de vermelho
                yell = 1
                return dur, yell
            else:
                self.set_yellow_phase(old_action, name)

            yell = 1
            dur = self.yellow_duration

        else:
            self.set_green_phase(action, name)
            dur = sapa.sapa_block(idx, routes, map_env, action)
            #dur = self.green_duration
            #print("DUR,action" dur, action)
            yell = 0
        return dur, yell


    def set_green_phase(self, action_number, TL_NAME):
        """
        Activate the correct green light combination in sumo
        """
        phase = [PHASE_NS_FD, PHASE_N_ALL, PHASE_S_ALL, PHASE_NS_LEFT, PHASE_WE_FD, PHASE_W_ALL, PHASE_E_ALL,
                 PHASE_WE_LEFT, PEDESTRIAN_PHASE]

        if action_number == 0:
            traci.trafficlight.setPhase(TL_NAME, phase[0])  # Action 0
        elif action_number == 1:
            traci.trafficlight.setPhase(TL_NAME, phase[1])  # Action 1
        elif action_number == 2:
            traci.trafficlight.setPhase(TL_NAME, phase[2])  # Action 2
        elif action_number == 3:
            traci.trafficlight.setPhase(TL_NAME, phase[3])  # Action 3
        elif action_number == 4:
            traci.trafficlight.setPhase(TL_NAME, phase[4])  # Action 4
        elif action_number == 5:
            traci.trafficlight.setPhase(TL_NAME, phase[5])  # Action 5
        elif action_number == 6:
            traci.trafficlight.setPhase(TL_NAME, phase[6])  # Action 6
        elif action_number == 7:
            traci.trafficlight.setPhase(TL_NAME, phase[7])  # Action 7
        elif action_number == 8:
            traci.trafficlight.setPhase(TL_NAME, phase[8])  # Action 8

    def set_yellow_phase(self, old_action, TL_NAME):
        """
        Activate the correct yellow light combination in sumo
        """
        yellow = [PHASE_NS_YELLOW, PHASE_N_ALL_YELLOW, PHASE_S_ALL_YELLOW, PHASE_NS_LEFT_YELLOW, PHASE_WE_FD_YELLOW,
                  PHASE_W_ALL_YELLOW, PHASE_E_ALL_YELLOW, PHASE_WE_LEFT_YELLOW, ALL_RED_PHASE]

        if old_action == 0:
            traci.trafficlight.setPhase(TL_NAME, yellow[0])  # Action 0
        elif old_action == 1:
            traci.trafficlight.setPhase(TL_NAME, yellow[1])  # Action 1
        elif old_action == 2:
            traci.trafficlight.setPhase(TL_NAME, yellow[2])  # Action 2
        elif old_action == 3:
            traci.trafficlight.setPhase(TL_NAME, yellow[3])  # Action 3
        elif old_action == 4:
            traci.trafficlight.setPhase(TL_NAME, yellow[4])  # Action 4
        elif old_action == 5:
            traci.trafficlight.setPhase(TL_NAME, yellow[5])  # Action 5
        elif old_action == 6:
            traci.trafficlight.setPhase(TL_NAME, yellow[6])  # Action 6
        elif old_action == 7:
            traci.trafficlight.setPhase(TL_NAME, yellow[7])  # Action 7
        elif old_action == 8:
            traci.trafficlight.setPhase(TL_NAME, yellow[8])  #Action 8


    def pedestrians_state(self, state, wz):
        """State observation for pedestrians in waiting zones"""

        for waiting_area in wz[0]:
            ped_list = traci.edge.getLastStepPersonIDs(waiting_area)
            #print("Pedestrians List on waiting Areas",ped_list, waiting_area)
            for ped in ped_list:
                laneId = traci.person.getLaneID(ped)
                speed = traci.person.getSpeed(ped)

                if laneId == wz[1][0] and speed < 0.1:
                    ped_position = 80
                    state[ped_position] = 1

                elif laneId == wz[1][1] and speed < 0.1:
                    ped_position = 81
                    state[ped_position] = 1

                elif laneId == wz[1][2] and speed < 0.1:
                    ped_position = 82
                    state[ped_position] = 1

                elif laneId == wz[1][3] and speed < 0.1:
                    ped_position = 83
                    state[ped_position] = 1

        return state

    def get_cell(self, pos, thresholds):
        for i, th in enumerate(thresholds):
            if pos < th:
                return i
        return len(thresholds) - 1

    def lane_group(self, route, lane):

        if lane == route[0]: #N1
            lane_group = 2
        elif lane == route[1]:#N2
            lane_group = 3
        elif lane == route[2]:#S1
            lane_group = 6
        elif lane == route[3]:#S2
            lane_group = 7
        elif lane == route[4]:#W1
            lane_group = 0
        elif lane == route[5]:#W2
            lane_group = 1
        elif lane == route[6]:#E1
            lane_group = 4
        elif lane == route[7]:#E2
            lane_group = 5
        else:
            lane_group = -1

        return lane_group

    def action_encode(self, state, action):


        if action == 0:
            phases = [1, 0, 0, 0, 0, 0, 0, 0, 0]
        elif action == 1:
            phases = [0, 1, 0, 0, 0, 0, 0, 0, 0]
        elif action == 2:
            phases = [0, 0, 1, 0, 0, 0, 0, 0, 0]
        elif action == 3:
            phases = [0, 0, 0, 1, 0, 0, 0, 0, 0]
        elif action == 4:
            phases = [0, 0, 0, 0, 1, 0, 0, 0, 0]
        elif action == 5:
            phases = [0, 0, 0, 0, 0, 1, 0, 0, 0]
        elif action == 6:
            phases = [0, 0, 0, 0, 0, 0, 1, 0, 0]
        elif action == 7:
            phases = [0, 0, 0, 0, 0, 0, 0, 1, 0]
        elif action == 8:
            phases = [0, 0, 0, 0, 0, 0, 0, 0, 1]
        else:
            phases = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        new_state = np.concatenate([state, phases])
        #assert len(new_state) == 173
        return new_state


    def get_state(self, idx, wz, routes, lanes_200_400, action):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """

        thresholds_200 = [7, 15, 25, 35, 55, 70, 100, 130, 150, 200]
        thresholds_400 = [7, 15, 25, 35, 55, 75, 100, 150, 200, 400]
        thresholds_100 = [7, 14, 20, 30, 40, 50, 60, 70, 80, 100]

        num_states_base = 164
        state = np.zeros(num_states_base)

        lane = routes[idx]
        lanes200 = lanes_200_400[0]
        lanes400 = lanes_200_400[1]

        for lane_id in lane:

            # determinar thresholds automaticamente
            if lane_id in lanes200:
                thresholds = thresholds_200
                lane_len = 200
            elif lane_id in lanes400:
                thresholds = thresholds_400
                lane_len = 400
            else:
                thresholds = thresholds_100
                lane_len = 100

            # carros nesta lane
            cars = traci.lane.getLastStepVehicleIDs(lane_id)
            #print("Lane", lane_id, "Carros na respetiva via->", cars)

            # obter grupo
            lane_group = self.lane_group(lane, lane_id)
            #print("Lane group", lane_group)
            if lane_group == -1:
                print("Wrong Lane Group")
                continue

            for car_id in cars:
                lane_pos = lane_len - traci.vehicle.getLanePosition(car_id)
                cell = self.get_cell(lane_pos, thresholds)

                cell_index = lane_group * 10 + cell
                speed_index = 84 + cell_index

                # ocupa cell
                state[cell_index] = 1

                # meter velocidade normalizada
                v = traci.vehicle.getSpeed(car_id)
                norm_v = v / 13.89
                state[speed_index] = (state[speed_index] + norm_v) / 2

        state = self.pedestrians_state(state, wz)

        state = self.action_encode(state, action)
    
        state = self.lane_occupancy(state, lane)

        return state


