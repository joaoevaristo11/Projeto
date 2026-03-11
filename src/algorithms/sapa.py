import traci

class sapa_module:
    def __init__(self):
        self.dur_base = 8
        self.priority_circular = 0.20 #prioridade dada à circular
        self.priority_radial = 0.20 #prioridade dada à radial
        self.not_priority = 0.25
        self._200_to_400 = 35
        self._400_to_200 = 20


    def sapa_block(self, idx, routes, map, action):

        if idx == 3 or idx == 7:
            return self.sapa_north_intersections(idx, routes, map, action)
        elif idx == 4 or idx == 8:
            return self.sapa_south_intersections(idx, routes, map, action)
        elif idx == 1 or idx == 5:
            return self.sapa_critic_intersections(idx, routes, map, action)
        elif idx == 0:
            return self.sapa_west_intersections(idx, routes, map, action)
        elif idx == 6:
            return self.sapa_east_intersections(idx, routes, map, action)
        elif idx == 2:
            return self.sapa_bothcells_intersections(idx, routes, map, action)

    def sapa_bothcells_intersections(self, idx, routes, map, action):
        idx_x = map[idx][0]  # cruzamento em questão C2
        idx_l = map[idx][1]  # cruzamento vizinho C1
        idx_r = map[idx][2]  #cruzamento vizinho c5

        route_intersection = routes[idx_x]
        route_neighbor_l = routes[idx_l]
        route_neighbor_r = routes[idx_r]

        if action == 0 or action == 1:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority

        elif action == 2:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("TL0, ação 2->", phaseTime)

        elif action == 3:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[3])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[1])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.not_priority
                # print("TL0, ação 3->", phaseTime)

        elif action == 4:  # passagem de 400 para 200 metros
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])

            if que_0 != 0:
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_l[6]) * 100
                # print("Tl2 a ver Ocupação em TL1", TL, occupancy_1)

                if occupancy_1 < self._200_to_400:  # passagem para uma via de 200 metros
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
                # print("phaseTime TL2 phase 4", phaseTime)
                else:
                    phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante
                # print("phaseTime TL2 phase 4", phaseTime)

            else:
                que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_r[4]) * 100
                if occupancy_1 < self._400_to_200:  # passagem para uma via de 200 metros
                    phaseTime = self.dur_base + self.dur_base * que_1 * self.priority_circular
                # print("phaseTime TL2 phase 4", phaseTime)
                else:
                    phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante
                # print("phaseTime TL2 phase 4", phaseTime)

        elif action == 5:  # Phase west
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
            # print("phaseTime TL2 phase 5", phaseTime)

        elif action == 6:  # Phase west
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_l[6]) * 100
            if occupancy_1 < self._200_to_400:  # passagem para uma via de 200 metros
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
            else:
                phaseTime = self.dur_base
            # print("phaseTime TL2 phase 5", phaseTime)

        elif action == 7:  # Phase W/E Left
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[5])
            if que_0 == 0:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[7])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL0 phase 7", phaseTime)

        else: #Pedestrians
            phaseTime = 10

        return round(phaseTime)

    def sapa_east_intersections(self, idx, routes, map, action):
        idx_x = map[idx][0]  # cruzamento em questão C6
        idx_y = map[idx][1]  # cruzamento vizinho C5

        route_intersection = routes[idx_x]
        route_neighbor = routes[idx_y]

        if action == 0 or action == 1:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority

        elif action == 2:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("TL0, ação 2->", phaseTime)

        elif action == 3:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[3])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[1])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.not_priority
                # print("TL0, ação 3->", phaseTime)

        elif action == 4:  # passagem de 100 para 400 metros
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            if que_0 != 0:
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[4]) * 100
                # print("Tl2 a ver Ocupação em TL1", TL, occupancy_1)
                if occupancy_1 < self._400_to_200:  # passagem para uma via de 200 metros, baixar a percentagem de ocupação
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
                    # print("phaseTime TL2 phase 4", phaseTime)
                else:
                    phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante
                    # print("phaseTime TL2 phase 4", phaseTime)
            else:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular

        elif action == 5:  # Phase West
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
            # print("phaseTime TL2 phase 5", phaseTime)

        elif action == 6:  # Phase east
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[6]) * 100
            if occupancy_1 < self._400_to_200:  # passagem para uma via de 200 metros
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
            else:
                phaseTime = self.dur_base

        elif action == 7:  # Phase W/E Left
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[5])
            if que_0 != 0:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL0 phase 7", phaseTime)
            else:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[7])
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority

        else: #Pedestrians
            phaseTime = 10

        return round(phaseTime)

    def sapa_west_intersections(self, idx, routes, map, action):

        idx_x = map[idx][0]  # cruzamento em questão C0
        idx_y = map[idx][1]  # cruzamento vizinho C1

        route_intersection = routes[idx_x]
        route_neighbor = routes[idx_y]

        if action == 0 or action == 1:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority

        elif action == 2:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("TL0, ação 2->", phaseTime)

        elif action == 3:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[3])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[1])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.not_priority
                # print("TL0, ação 3->", phaseTime)

        elif action == 4:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            if que_0 != 0:
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[4]) * 100
                if occupancy_1 < self._400_to_200:
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
                else:
                    phaseTime = self.dur_base
            else:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular

        elif action == 5:  # passagem de 100 para 400 metros
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[4]) * 100
            if occupancy_1 < self._400_to_200:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
            else:
                phaseTime = self.dur_base

        elif action == 6:  # Phase East
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
            # print("phaseTime TL0 phase 6", phaseTime)

        elif action == 7:  # Phase W/E Left
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[7])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL0 phase 7", phaseTime)

        else: #Pedestrians
            phaseTime = 10

        return round(phaseTime)

    def sapa_critic_intersections(self, idx, routes, map, action):

        idx_x = map[idx][0]  # cruzamento em questão C1 ou C5
        idx_l = map[idx][1]  # cruzamento vizinho C0 ou C2
        idx_r = map[idx][2]  # cruzamento vizinho C2 ou C6
        idx_n = map[idx][3]  # cruzamento vizinho C3 ou C7
        idx_s = map[idx][4]  # cruzamento vizinho C4 ou C8

        route_intersection = routes[idx_x]
        route_neighbor_l = routes[idx_l]
        route_neighbor_r = routes[idx_r]
        route_neighbor_n = routes[idx_n]
        route_neighbor_s = routes[idx_s]

        if action == 0:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2]) #south lane of c1 or c5
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[0]) #north lane of c1 or c5
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_n[2]) * 100 #south lane ocuppancy of c3 or c7
            occupancy_2 = traci.lane.getLastStepOccupancy(route_neighbor_s[0]) * 100 #north lane ocuppancy of c4 or c8
            if que_0 > que_1:
                if occupancy_1 > self._400_to_200:  # passagem para 200 metros ...
                    phaseTime = self.dur_base
                else:
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
            else:
                if occupancy_2 > self._400_to_200:  # going to a lane of 400 but only 20% because of south movements N-S Action
                    phaseTime = self.dur_base
                else:
                    phaseTime = self.dur_base + self.dur_base * que_1 * self.priority_radial

                # print("TL, ação 0->", phaseTime)

        elif action == 1:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
            # print("TL3, ação 1->", phaseTime)

        elif action == 2:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_n[2]) * 100
            if occupancy_1 > self._400_to_200:  # passagem para 200 metros ...
                phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante
            else:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial

        elif action == 3:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[3])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[1])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.priority_radial
            # print("TL0, ação 3->", phaseTime)

        elif action == 4:  # passagem de 400 para 200 atenção
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            if que_0 != 0:
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_r[4]) * 100
            # print("TL1 a ver ocupação em tl2", TL, occupancy_1)
                if occupancy_1 < self._400_to_200:  # 200 metros então baixara ocupação
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
                # print("phaseTime", phaseTime)
                else:
                    phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante
                # print("phaseTime", phaseTime)
            else:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_l[6]) * 100
                if occupancy_1 < self._200_to_400:  #going to a 400m lane
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
                else:
                    phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante

        elif action == 5:  # passagem de 400 para 200 atenção
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor_r[4]) * 100
            # print("TL1 a ver ocupação em tl2", TL, occupancy_1)
            if occupancy_1 < self._400_to_200:  # 200 metros então baixara ocupação
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular
                # print("phaseTime", phaseTime)
            else:
                phaseTime = self.dur_base  # + dur_base * que_0 * percentagem_menosImportante
                # print("phaseTime", phaseTime)

        elif action == 6:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_circular

        elif action == 7:  # passagem de 100 para 400 metros
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[5])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[7])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.not_priority
            # print("TL, ação 7->", phaseTime)

        else: #Pedestrians
            phaseTime = 10 #10 segundos de verde

        return round(phaseTime)

    def sapa_north_intersections(self, idx, routes, map, action):

        idx_x = map[idx][0] #cruzamento em questão C3 ou C7
        idx_y = map[idx][1] #cruzamento vizinho C1 ou C5

        route_intersection = routes[idx_x]
        route_neighbor = routes[idx_y]

        #N-S Action
        if action == 0:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            if que_0 != 0:
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[0]) * 100
                if occupancy_1 < self._400_to_200:  # para uma via de 200 metros atenção
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
                else:
                    phaseTime = self.dur_base
            else:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial

        #N Action
        elif action == 1:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[0]) * 100
            if occupancy_1 < self._400_to_200:  # para uma via de 200 metros atenção
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
            else:
                phaseTime = self.dur_base

        #South Action
        elif action == 2:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial

        #N-S Left Action
        elif action == 3:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[3])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[1])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.not_priority

        #W-E, W Action
        elif action == 4 or action == 5:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL3 phase 4", phaseTime)

        #E Action
        elif action == 6:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL3 phase 6", phaseTime)

        #W/E Left Action
        elif action == 7:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[5])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL3 phase 7", phaseTime)

        else: #Pedestrians
            phaseTime = 10 #10 segundos de verde

        return round(phaseTime)

    def sapa_south_intersections(self, idx, routes, map, action):

        idx_x = map[idx][0]  # cruzamento em questão C4 ou C8
        idx_y = map[idx][1]  # cruzamento vizinho C1 ou C5

        route_intersection = routes[idx_x]
        route_neighbor = routes[idx_y]

        #N-S Action
        if action == 0:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            if que_0 != 0:
                occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[2]) * 100
                if occupancy_1 < self._200_to_400:
                    phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
                else:
                    phaseTime = self.dur_base
            else:
                que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial

        #S Action
        elif action == 2:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[2])
            occupancy_1 = traci.lane.getLastStepOccupancy(route_neighbor[2]) * 100
            if occupancy_1 < self._200_to_400: # going to a 400 m lane
                phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial
            else:
                phaseTime = self.dur_base
        #N Action
        elif action == 1:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[0])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.priority_radial

        #N-S Action
        elif action == 3:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[1])
            que_1 = traci.lane.getLastStepHaltingNumber(route_intersection[3])
            if que_0 > que_1 or que_0 == que_1:
                phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            else:
                phaseTime = self.dur_base + self.dur_base * que_1 * self.not_priority
            # print("TL4, ação 3->", phaseTime)

        #W-E, W Action
        elif action == 4 or action == 5:
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[4])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority

        #E Action
        elif action == 6:  # Phase East
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[6])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL4 phase 6", phaseTime)
            return round(phaseTime)

        #W-E Left
        elif action == 7:  # Phase W/E Left
            que_0 = traci.lane.getLastStepHaltingNumber(route_intersection[5])
            phaseTime = self.dur_base + self.dur_base * que_0 * self.not_priority
            # print("phaseTime TL4 phase 7", phaseTime)

        else: #Pedestrians
            phaseTime = 10 #10 segundos de verde

        return round(phaseTime)
