import numpy as np
import math
import matplotlib.pyplot as plt


class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated, scenario):
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
        self._scenario = scenario

        self._circular_prob, self._in_out_prob = self.get_probs_by_scenario(self._scenario)

    def get_probs_by_scenario(self, scenario):
        # circular_prob : prob. de usar artéria horizontal (EG/VV) vs. vertical (MT/510)
        # in_out_prob   : prob. de movimento Norte->Sul vs. Sul->Norte
        #
        # Cenário 6 — dados reais recolhidos no terreno (hora de ponta 17h30-18h30):
        #   circular_prob = 0.286  (28.6% do tráfego é horizontal)
        #   in_out_prob   = 0.448  (44.8% do vertical é NS, 55.2% é SN)
        #   Total médio   ~ 4204 veículos/hora
        #   Fonte: contagens manuais e por vídeo na zona do IMT, março 2026
        scenario_probs = {
            1: (0.50, 0.50),   # equilibrado
            2: (0.65, 0.75),   # hora de ponta manhã
            3: (0.65, 0.25),   # hora de ponta tarde
            4: (0.25, 0.75),
            5: (0.25, 0.25),
            6: (0.29, 0.45),   # REAL: hora de ponta (dados terreno IMT, março 2026)
        }
        if scenario not in scenario_probs:
            raise ValueError(f"Cenário inválido: {scenario}. Deve ser um número entre 1 e 6.")
        return scenario_probs[scenario]

    def generate_routefile(self, seed):
        """
        Generation of the route of every car for one episode
        """
        np.random.seed(seed)  # make tests reproducible

        # the generation of cars is distributed according to a weibull distribution
        timings = np.random.weibull(2, self._n_cars_generated)
        timings = np.sort(timings)

        # reshape the distribution to fit the interval 0:max_steps
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = self._max_steps

        for value in timings:
            novo_valor = ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new
            car_gen_steps = np.append(car_gen_steps, novo_valor)

        # Arredondar os passos para inteiros
        car_gen_steps = np.rint(car_gen_steps)

        # produce the file for cars generation, one car per line
        with open("sumo/episode_routes.rou.xml", "w") as routes:
            print("""<routes>
            <vType accel="1.0" decel="4.5" id="standard_car" length="5.0" minGap="2.5" maxSpeed="13.9" depart_speed = "13.9" sigma="0.5" />

            <!-- Artéria circular horizontal: Av. Elias Garcia (EG) -->
            <!-- Oeste -> Este -->
            <route id="EG_W_recto"  edges="EG_WE_1 EG_WE_2 EG_WE_3"/>
            <route id="EG_W_MT_S"   edges="EG_WE_1 MT_NS_2 MT_NS_3"/>
            <route id="EG_W_MT_N"   edges="EG_WE_1 MT_SN_3"/>
            <route id="EG_W_510_S"  edges="EG_WE_1 EG_WE_2 510_NS_2 510_NS_3"/>
            <route id="EG_W_510_N"  edges="EG_WE_1 EG_WE_2 510_SN_3"/>
            <!-- Este -> Oeste -->
            <route id="EG_E_recto"  edges="EG_EW_1 EG_EW_2 EG_EW_3"/>
            <route id="EG_E_510_S"  edges="EG_EW_1 510_NS_2 510_NS_3"/>
            <route id="EG_E_510_N"  edges="EG_EW_1 510_SN_3"/>
            <route id="EG_E_MT_S"   edges="EG_EW_1 EG_EW_2 MT_NS_2 MT_NS_3"/>
            <route id="EG_E_MT_N"   edges="EG_EW_1 EG_EW_2 MT_SN_3"/>

            <!-- Artéria circular horizontal: Av. Visconde de Valmor (VV) -->
            <!-- Oeste -> Este -->
            <route id="VV_W_recto"  edges="VV_WE_1 VV_WE_2 VV_WE_3"/>
            <route id="VV_W_MT_N"   edges="VV_WE_1 MT_SN_2 MT_SN_3"/>
            <route id="VV_W_MT_S"   edges="VV_WE_1 MT_NS_3"/>
            <route id="VV_W_510_S"  edges="VV_WE_1 VV_WE_2 510_NS_3"/>
            <route id="VV_W_510_N"  edges="VV_WE_1 VV_WE_2 510_SN_2 510_SN_3"/>
            <!-- Este -> Oeste -->
            <route id="VV_E_recto"  edges="VV_EW_1 VV_EW_2 VV_EW_3"/>
            <route id="VV_E_510_S"  edges="VV_EW_1 510_NS_3"/>
            <route id="VV_E_510_N"  edges="VV_EW_1 510_SN_2 510_SN_3"/>
            <route id="VV_E_MT_S"   edges="VV_EW_1 VV_EW_2 MT_NS_3"/>
            <route id="VV_E_MT_N"   edges="VV_EW_1 VV_EW_2 MT_SN_2 MT_SN_3"/>

            <!-- Artéria radial vertical: Av. Marquês de Tomar (MT) -->
            <!-- Norte -> Sul -->
            <route id="MT_N_recto"  edges="MT_NS_1 MT_NS_2 MT_NS_3"/>
            <route id="MT_N_EG_E"   edges="MT_NS_1 EG_WE_2 EG_WE_3"/>
            <route id="MT_N_EG_W"   edges="MT_NS_1 EG_EW_3"/>
            <route id="MT_N_VV_E"   edges="MT_NS_1 MT_NS_2 VV_WE_2 VV_WE_3"/>
            <route id="MT_N_VV_W"   edges="MT_NS_1 MT_NS_2 VV_EW_3"/>
            <!-- Sul -> Norte -->
            <route id="MT_S_recto"  edges="MT_SN_1 MT_SN_2 MT_SN_3"/>
            <route id="MT_S_VV_E"   edges="MT_SN_1 VV_WE_2 VV_WE_3"/>
            <route id="MT_S_VV_W"   edges="MT_SN_1 VV_EW_3"/>
            <route id="MT_S_EG_E"   edges="MT_SN_1 MT_SN_2 EG_WE_2 EG_WE_3"/>
            <route id="MT_S_EG_W"   edges="MT_SN_1 MT_SN_2 EG_EW_3"/>

            <!-- Artéria radial vertical: Av. 5 de Outubro (510) -->
            <!-- Norte -> Sul -->
            <route id="C510_N_recto" edges="510_NS_1 510_NS_2 510_NS_3"/>
            <route id="C510_N_EG_W"  edges="510_NS_1 EG_EW_2 EG_EW_3"/>
            <route id="C510_N_EG_E"  edges="510_NS_1 EG_WE_3"/>
            <route id="C510_N_VV_W"  edges="510_NS_1 510_NS_2 VV_EW_2 VV_EW_3"/>
            <route id="C510_N_VV_E"  edges="510_NS_1 510_NS_2 VV_WE_3"/>
            <!-- Sul -> Norte -->
            <route id="C510_S_recto" edges="510_SN_1 510_SN_2 510_SN_3"/>
            <route id="C510_S_VV_W"  edges="510_SN_1 VV_EW_2 VV_EW_3"/>
            <route id="C510_S_VV_E"  edges="510_SN_1 VV_WE_3"/>
            <route id="C510_S_EG_W"  edges="510_SN_1 510_SN_2 EG_EW_2 EG_EW_3"/>
            <route id="C510_S_EG_E"  edges="510_SN_1 510_SN_2 EG_WE_3"/>""", file=routes)

            # Probabilidades derivadas dos dados reais (hora de ponta, zona IMT):
            #
            # Horizontal (EG vs VV): EG=74.2%, VV=25.8%  → eg_prob = 0.742
            # Dentro EG: OE=44.7%, EO=55.3%              → eg_west_east = 0.447
            # Dentro VV: OE=51.9%, EO=48.1%              → vv_west_east = 0.519
            # Vertical (MT vs 510): MT=37.4%, 510=62.6%  → mt_prob = 0.374
            # MT  NS/SN: 41.7% / 58.3%                   → mt_in_out = 0.417
            # 510 NS/SN: 46.6% / 53.4%                   → c510_in_out = 0.466

            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()
                if straight_or_turn < 0.75:  # choose direction: straight or turn - 75% of times the car goes straight
                    arterial_routes = np.random.uniform()
                    if arterial_routes < self._circular_prob:  # Artéria circular (EG ou VV)
                        eg_or_vv = np.random.uniform()
                        if eg_or_vv < 0.742:  # Av. Elias Garcia (74.2% do horizontal)
                            west_east_routes = np.random.uniform()
                            if west_east_routes < 0.447:  # Oeste -> Este (44.7%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="EG_W_recto_%i" type="standard_car" route="EG_W_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="EG_W_MT_S_%i" type="standard_car" route="EG_W_MT_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="EG_W_MT_N_%i" type="standard_car" route="EG_W_MT_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="EG_W_510_S_%i" type="standard_car" route="EG_W_510_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="EG_W_510_N_%i" type="standard_car" route="EG_W_510_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:  # Este -> Oeste (55.3%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="EG_E_recto_%i" type="standard_car" route="EG_E_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="EG_E_510_S_%i" type="standard_car" route="EG_E_510_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="EG_E_510_N_%i" type="standard_car" route="EG_E_510_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="EG_E_MT_S_%i" type="standard_car" route="EG_E_MT_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="EG_E_MT_N_%i" type="standard_car" route="EG_E_MT_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                        else:  # Av. Visconde de Valmor (25.8% do horizontal)
                            west_east_routes = np.random.uniform()
                            if west_east_routes < 0.519:  # Oeste -> Este (51.9%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="VV_W_recto_%i" type="standard_car" route="VV_W_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="VV_W_MT_N_%i" type="standard_car" route="VV_W_MT_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="VV_W_MT_S_%i" type="standard_car" route="VV_W_MT_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="VV_W_510_S_%i" type="standard_car" route="VV_W_510_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="VV_W_510_N_%i" type="standard_car" route="VV_W_510_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:  # Este -> Oeste (48.1%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="VV_E_recto_%i" type="standard_car" route="VV_E_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="VV_E_510_S_%i" type="standard_car" route="VV_E_510_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="VV_E_510_N_%i" type="standard_car" route="VV_E_510_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="VV_E_MT_S_%i" type="standard_car" route="VV_E_MT_S" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="VV_E_MT_N_%i" type="standard_car" route="VV_E_MT_N" depart="%s" departLane="best" />' % (car_counter, step), file=routes)

                    else:  # Artéria radial (MT ou 510)
                        mt_or_510 = np.random.uniform()
                        if mt_or_510 < 0.374:  # Av. Marquês de Tomar (37.4% do vertical)
                            in_out_priority = np.random.uniform()
                            if in_out_priority < 0.417:  # Norte -> Sul (41.7%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="MT_N_recto_%i" type="standard_car" route="MT_N_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="MT_N_EG_E_%i" type="standard_car" route="MT_N_EG_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="MT_N_EG_W_%i" type="standard_car" route="MT_N_EG_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="MT_N_VV_E_%i" type="standard_car" route="MT_N_VV_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="MT_N_VV_W_%i" type="standard_car" route="MT_N_VV_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:  # Sul -> Norte (58.3%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="MT_S_recto_%i" type="standard_car" route="MT_S_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="MT_S_VV_E_%i" type="standard_car" route="MT_S_VV_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="MT_S_VV_W_%i" type="standard_car" route="MT_S_VV_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="MT_S_EG_E_%i" type="standard_car" route="MT_S_EG_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="MT_S_EG_W_%i" type="standard_car" route="MT_S_EG_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                        else:  # Av. 5 de Outubro (62.6% do vertical)
                            in_out_priority = np.random.uniform()
                            if in_out_priority < 0.466:  # Norte -> Sul (46.6%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="C510_N_recto_%i" type="standard_car" route="C510_N_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="C510_N_EG_W_%i" type="standard_car" route="C510_N_EG_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="C510_N_EG_E_%i" type="standard_car" route="C510_N_EG_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="C510_N_VV_W_%i" type="standard_car" route="C510_N_VV_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="C510_N_VV_E_%i" type="standard_car" route="C510_N_VV_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:  # Sul -> Norte (53.4%)
                                route_straight = np.random.randint(1, 6)
                                if route_straight == 1:
                                    print('    <vehicle id="C510_S_recto_%i" type="standard_car" route="C510_S_recto" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="C510_S_VV_W_%i" type="standard_car" route="C510_S_VV_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 3:
                                    print('    <vehicle id="C510_S_VV_E_%i" type="standard_car" route="C510_S_VV_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 4:
                                    print('    <vehicle id="C510_S_EG_W_%i" type="standard_car" route="C510_S_EG_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                else:
                                    print('    <vehicle id="C510_S_EG_E_%i" type="standard_car" route="C510_S_EG_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)

                else:  # viragem local (25% dos carros) — percursos curtos dentro da rede
                    route_turn = np.random.randint(1, 17)
                    if route_turn == 1:
                        print('    <vehicle id="MT_N_EG_E_%i" type="standard_car" route="MT_N_EG_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                    elif route_turn == 2:
                        print('    <vehicle id="MT_N_EG_W_%i" type="standard_car" route="MT_N_EG_W" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 3:
                        print('    <vehicle id="MT_S_VV_E_%i" type="standard_car" route="MT_S_VV_E" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 4:
                        print('    <vehicle id="MT_S_VV_W_%i" type="standard_car" route="MT_S_VV_W" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 5:
                        print('    <vehicle id="EG_W_MT_S_%i" type="standard_car" route="EG_W_MT_S" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 6:
                        print('    <vehicle id="EG_W_MT_N_%i" type="standard_car" route="EG_W_MT_N" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 7:
                        print('    <vehicle id="EG_E_510_S_%i" type="standard_car" route="EG_E_510_S" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 8:
                        print('    <vehicle id="EG_E_510_N_%i" type="standard_car" route="EG_E_510_N" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 9:
                        print('    <vehicle id="VV_W_MT_N_%i" type="standard_car" route="VV_W_MT_N" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 10:
                        print('    <vehicle id="VV_W_MT_S_%i" type="standard_car" route="VV_W_MT_S" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 11:
                        print('    <vehicle id="VV_E_510_S_%i" type="standard_car" route="VV_E_510_S" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 12:
                        print('    <vehicle id="VV_E_510_N_%i" type="standard_car" route="VV_E_510_N" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 13:
                        print('    <vehicle id="C510_N_EG_W_%i" type="standard_car" route="C510_N_EG_W" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 14:
                        print('    <vehicle id="C510_N_EG_E_%i" type="standard_car" route="C510_N_EG_E" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 15:
                        print('    <vehicle id="C510_S_VV_W_%i" type="standard_car" route="C510_S_VV_W" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    else:
                        print('    <vehicle id="C510_S_VV_E_%i" type="standard_car" route="C510_S_VV_E" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)

            print("</routes>", file=routes)