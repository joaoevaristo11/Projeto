import traci


class sapa_module:
    def __init__(self):
        self.dur_base = 8
        self.priority_ns = 0.20   # prioridade eixo vertical (MT/510)
        self.priority_ew = 0.20   # prioridade eixo horizontal (EG/VV)

    def sapa_block(self, idx, routes, map_env, action):
        """
        Calcula a duracao da fase para cada cruzamento.

        Rede IMT — 4 cruzamentos, 2 acoes:
          action 0 -> verde NS (Norte-Sul, eixo vertical)
          action 1 -> verde EW (Este-Oeste, eixo horizontal)

        Routes por cruzamento (edges de entrada):
          J1 (idx=1): [MT_NS_1, EG_WE_1, MT_SN_2, EG_EW_2]  -> 4 edges
          J2 (idx=2): [510_NS_1_1, 510_NS_1_2, EG_EW_1, EG_WE_2, 510_SN_2_1, 510_SN_2_2] -> 6 edges
          J3 (idx=3): [MT_NS_2, VV_WE_1, VV_EW_2, MT_SN_1]  -> 4 edges
          J4 (idx=4): [510_NS_2_1, 510_NS_2_2, VV_EW_1, VV_WE_2, 510_SN_1_1, 510_SN_1_2] -> 6 edges

        Para routes de 4 edges:
          [0]=N, [1]=W, [2]=S, [3]=E
        Para routes de 6 edges:
          [0]=N1, [1]=N2, [2]=W, [3]=E, [4]=S1, [5]=S2
        """
        route = routes[map_env[idx][0]]
        n = len(route)

        # Identificar edges NS e EW conforme o tamanho da route
        if n == 4:
            # J1, J3: [N, W, S, E]
            edges_ns = [route[0], route[2]]  # Norte e Sul
            edges_ew = [route[1], route[3]]  # Oeste e Este
        else:
            # J2, J4: [N1, N2, W, E, S1, S2]
            edges_ns = [route[0], route[1], route[4], route[5]]  # Norte e Sul (2 faixas cada)
            edges_ew = [route[2], route[3]]                       # Oeste e Este

        # Calcular filas para cada eixo usando edges (nao lanes)
        queue_ns = sum(traci.edge.getLastStepHaltingNumber(e) for e in edges_ns)
        queue_ew = sum(traci.edge.getLastStepHaltingNumber(e) for e in edges_ew)

        # Ver ocupacao do cruzamento vizinho se existir
        neighbor_idx = map_env[idx][1] if len(map_env[idx]) > 1 else None
        neighbor_occupancy = 0.0
        if neighbor_idx is not None and neighbor_idx in routes:
            neighbor_route = routes[neighbor_idx]
            neighbor_n = len(neighbor_route)
            if neighbor_n == 4:
                neighbor_edges = [neighbor_route[0], neighbor_route[2]]
            else:
                neighbor_edges = [neighbor_route[0], neighbor_route[1], neighbor_route[4], neighbor_route[5]]
            total_occ = sum(traci.edge.getLastStepOccupancy(e) for e in neighbor_edges)
            neighbor_occupancy = (total_occ / len(neighbor_edges)) * 100

        if action == 0:  # Verde NS
            if neighbor_occupancy > 35:
                # vizinho congestionado, nao prolongar muito
                phaseTime = self.dur_base
            else:
                phaseTime = self.dur_base + self.dur_base * queue_ns * self.priority_ns

        elif action == 1:  # Verde EW
            if neighbor_occupancy > 35:
                phaseTime = self.dur_base
            else:
                phaseTime = self.dur_base + self.dur_base * queue_ew * self.priority_ew

        else:
            phaseTime = self.dur_base

        return round(phaseTime)