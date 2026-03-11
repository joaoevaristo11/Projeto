import numpy as np
import math
import matplotlib.pyplot as plt


class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated, scenario):
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
        self._scenario = scenario

        self._circular_prob, self._in_out_prob = self.get_probs_by_scenario(self._scenario)
        # print(self._circular_prob, self._in_out_prob)

    def get_probs_by_scenario(self, scenario):
        scenario_probs = {
            1: (0.50, 0.50),
            2: (0.65, 0.75),
            3: (0.65, 0.25),
            4: (0.25, 0.75),
            5: (0.25, 0.25)
        }
        if scenario not in scenario_probs:
            raise ValueError(f"Cenário inválido: {scenario}. Deve ser um número entre 1 e 5.")
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
            
            <route id="W_E" edges="W_TL0 TL0_TL TL_TL2 TL2_TL5 TL5_TL6 TL6_E"/>
            <route id="W_S4" edges="W_TL0 TL0_TL TL_TL4 TL4_S"/>
            <route id="W_S2" edges="W_TL0 TL0_TL TL_TL2 TL2_S"/>
            <route id="W_S8" edges="W_TL0 TL0_TL TL_TL2 TL2_TL5 TL5_TL8 TL8_S"/>
            
            <route id="W_W3" edges="W_TL0 TL0_TL TL_TL3 TL3_W"/>
            <route id="W_N2" edges="W_TL0 TL0_TL TL_TL2 TL2_N"/>
            <route id="W_N6" edges="W_TL0 TL0_TL TL_TL2 TL2_TL5 TL5_TL6 TL6_N"/>
            
            <route id="E_W" edges="E_TL6 TL6_TL5 TL5_TL2 TL2_TL TL_TL0 TL0_W"/>
            <route id="E_N7" edges="E_TL6 TL6_TL5 TL5_TL7 TL7_N"/>
            <route id="E_N2" edges="E_TL6 TL6_TL5 TL5_TL2 TL2_N"/>
            <route id="E_N3" edges="E_TL6 TL6_TL5 TL5_TL2 TL2_TL TL_TL3 TL3_N"/>
            
            <route id="E_E8" edges="E_TL6 TL6_TL5 TL5_TL8 TL8_E"/>
            <route id="E_S2" edges="E_TL6 TL6_TL5 TL5_TL2 TL2_S"/>
            <route id="E_S0" edges="E_TL6 TL6_TL5 TL5_TL2 TL2_TL TL_TL0 TL0_S"/>
            
            <route id="N3_S4" edges="N_TL3 TL3_TL TL_TL4 TL4_S"/>
            <route id="N3_W3" edges="N_TL3 TL3_W"/>
            <route id="N3_E4" edges="N_TL3 TL3_TL TL_TL4 TL4_E"/>
            <route id="S4_N3" edges="S_TL4 TL4_TL TL_TL3 TL3_N"/>
            <route id="S4_E3" edges="S_TL4 TL4_TL TL_TL3 TL3_E"/>
            <route id="S4_W0" edges="S_TL4 TL4_TL TL_TL0 TL0_W"/>
            
            <route id="N7_S8" edges="N_TL7 TL7_TL5 TL5_TL8 TL8_S"/>
            <route id="N7_E6" edges="N_TL7 TL7_TL5 TL5_TL6 TL6_E"/>
            <route id="N7_E8" edges="N_TL7 TL7_TL5 TL5_TL8 TL8_E"/>
            <route id="S8_N7" edges="S_TL8 TL8_TL5 TL5_TL7 TL7_N"/>
            <route id="S8_W7" edges="S_TL8 TL8_TL5 TL5_TL7 TL7_W"/>
            <route id="S8_N2" edges="S_TL8 TL8_TL5 TL5_TL2 TL2_N"/>
            
            
            
            
            <route id="N0_S0" edges="N_TL0 TL0_S"/>
            <route id="S0_N0" edges="S_TL0 TL0_N"/>
            
            <route id="N6_S6" edges="N_TL6 TL6_S"/>
            <route id="S6_N6" edges="S_TL6 TL6_N"/>
            
            <route id="N2_S2" edges="N_TL2 TL2_S"/>
            <route id="S2_N2" edges="S_TL2 TL2_N"/>
            
            <route id="W3_E3" edges="W_TL3 TL3_E"/>
            <route id="E3_W3" edges="E_TL3 TL3_W"/>
            
            <route id="W4_E4" edges="W_TL4 TL4_E"/>
            <route id="E4_W4" edges="E_TL4 TL4_W"/>
            
            <route id="W7_E7" edges="W_TL7 TL7_E"/>
            <route id="E7_W7" edges="E_TL7 TL7_W"/>
            
            <route id="W8_E8" edges="W_TL8 TL8_E"/>
            <route id="E8_W8" edges="E_TL8 TL8_W"/>
            
            <route id="N0_L" edges="N_TL0 TL0_TL TL_TL3 TL3_W"/>
            <route id="W0_L" edges="W_TL0 TL0_N"/>
            <route id="S0_L" edges="S_TL0 TL0_W"/>
            
            <route id="S6_L" edges="S_TL6 TL6_TL5 TL5_TL8 TL8_E"/>
            <route id="N6_L" edges="N_TL6 TL6_E"/>
            <route id="E6_L" edges="E_TL6 TL6_S"/>
            
            <route id="W3_L" edges="W_TL3 TL3_N"/>
            <route id="E3_L" edges="E_TL3 TL3_TL TL_TL2 TL2_N"/>
            <route id="N3_L" edges="N_TL3 TL3_E"/>
            
            <route id="S4_L" edges="S_TL4 TL4_W"/>
            <route id="E4_L" edges="E_TL4 TL4_S"/>
            <route id="W4_L" edges="W_TL4 TL4_TL TL_TL0 TL0_S"/>
            
            <route id="S8_L" edges="S_TL8 TL8_W"/>
            <route id="E8_L" edges="E_TL8 TL8_S"/>
            <route id="W8_L" edges="W_TL8 TL8_TL5 TL5_TL2 TL2_S"/>
            
            <route id="S2_L" edges="S_TL2 TL2_TL TL_TL4 TL4_E"/>
            <route id="N2_L" edges="N_TL2 TL2_TL5 TL5_TL7 TL7_W"/>""", file=routes)

            #cenario = [[0.50, 0.50], [0.65, 0.75], [0.65, 0.25], [0.35, 0.75], [0.35, 0.35]]

            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()
                if straight_or_turn < 0.75:  # choose direction: straight or turn - 75% of times the car goes straight
                    arterial_routes = np.random.uniform()
                    if arterial_routes < self._circular_prob:# Artéria circular
                        west_east_routes = np.random.uniform()
                        if west_east_routes < 0.50:
                            route_straight = np.random.randint(1, 8)
                            if route_straight == 1:
                                print('    <vehicle id="W_E_%i" type="standard_car" route="W_E" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 2:
                                print('    <vehicle id="W_S4_%i" type="standard_car" route="W_S4" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 3:
                                print('    <vehicle id="W_S2_%i" type="standard_car" route="W_S2" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            #elif route_straight == 4:
                                #print('    <vehicle id="W_W3_%i" type="standard_car" route="W_W3" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 4:
                                print('    <vehicle id="W_N2_%i" type="standard_car" route="W_N2" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 5:
                                print('    <vehicle id="W_N6_%i" type="standard_car" route="W_N6" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:
                                print('    <vehicle id="W_S8_%i" type="standard_car" route="W_S8" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                        else:
                            route_straight = np.random.randint(1, 8)
                            if route_straight == 1:
                                print('    <vehicle id="E_W_%i" type="standard_car" route="E_W" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 2:
                                print('    <vehicle id="E_N7_%i" type="standard_car" route="E_N7" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 3:
                                print('    <vehicle id="E_N2_%i" type="standard_car" route="E_N2" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 4:
                                print('    <vehicle id="E_E8_%i" type="standard_car" route="E_E8" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 5:
                                print('    <vehicle id="E_S2_%i" type="standard_car" route="E_S2" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            elif route_straight == 6:
                                print('    <vehicle id="E_S0_%i" type="standard_car" route="E_S0" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:
                                print('    <vehicle id="E_N3_%i" type="standard_car" route="E_N3" depart="%s" departLane="best" />' % (car_counter, step), file=routes)

                    else: #artéria radial
                        cell = np.random.uniform()
                        if cell < 0.80: #célula 1
                            in_out_priority = np.random.uniform()
                            if in_out_priority < self._in_out_prob: #priority out
                                route_straight = np.random.randint(1, 3)
                                if route_straight == 1:
                                    print('    <vehicle id="S4_N3_%i" type="standard_car" route="S4_N3" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="S4_E3_%i" type="standard_car" route="S4_E3" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                # elif route_straight == 3:
                                #     print('    <vehicle id="S4_W0_%i" type="standard_car" route="S4_W0" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else: #priority in
                                route_straight = np.random.randint(1, 4)
                                if route_straight == 1:
                                    print('    <vehicle id="N3_S4_%i" type="standard_car" route="N3_S4" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="N3_E4_%i" type="standard_car" route="N3_E4" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                if route_straight == 3:
                                    print('    <vehicle id="N3_W3_%i" type="standard_car" route="N3_W3" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                        else:
                            in_out_priority = np.random.uniform()
                            if in_out_priority < self._in_out_prob:  # priority out
                                route_straight = np.random.randint(1, 3)
                                if route_straight == 1:
                                    print('    <vehicle id="S8_N7_%i" type="standard_car" route="S8_N7" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="S8_E7_%i" type="standard_car" route="S8_W7" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                # elif route_straight == 3:
                                #     print('    <vehicle id="S8_N2_%i" type="standard_car" route="S8_N2" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                            else:  # priority in
                                route_straight = np.random.randint(1, 3)
                                if route_straight == 1:
                                    print('    <vehicle id="N7_S8_%i" type="standard_car" route="N7_S8" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                # elif route_straight == 2:
                                #    print('    <vehicle id="N7_E6_%i" type="standard_car" route="N7_E6" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                                elif route_straight == 2:
                                    print('    <vehicle id="N7_E8_%i" type="standard_car" route="N7_E8" depart="%s" departLane="best" />' % (car_counter, step), file=routes)

                else:
                    route_turn = np.random.randint(1, 33)  # choose random source & destination
                    if route_turn == 1:
                        print('    <vehicle id="N0_S0_%i" type="standard_car" route="N0_S0" depart="%s" departLane="best" />' % (car_counter, step), file=routes)
                    elif route_turn == 2:
                        print('    <vehicle id="S0_N0_%i" type="standard_car" route="S0_N0" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 3:
                        print('    <vehicle id="N6_S6_%i" type="standard_car" route="N6_S6" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 4:
                        print('    <vehicle id="S6_N6_%i" type="standard_car" route="S6_N6" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 5:
                        print('    <vehicle id="N2_S2_%i" type="standard_car" route="N2_S2" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 6:
                        print('    <vehicle id="S2_N2_%i" type="standard_car" route="S2_N2" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 7:
                        print('    <vehicle id="W3_E3_%i" type="standard_car" route="W3_E3" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 8:
                        print('    <vehicle id="E3_W3_%i" type="standard_car" route="E3_W3" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 9:
                        print('    <vehicle id="W4_E4_%i" type="standard_car" route="W4_E4" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 10:
                        print('    <vehicle id="E4_W4_%i" type="standard_car" route="E4_W4" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 11:
                        print('    <vehicle id="W7_E7_%i" type="standard_car" route="W7_E7" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 12:
                        print('    <vehicle id="E7_W7_%i" type="standard_car" route="E7_W7" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 13:
                        print('    <vehicle id="W8_E8_%i" type="standard_car" route="W8_E8" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 14:
                        print('    <vehicle id="E8_W8_%i" type="standard_car" route="E8_W8" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)

                    elif route_turn == 16:
                        print('    <vehicle id="N0_L_%i" type="standard_car" route="N0_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 17:
                        print('    <vehicle id="S0_L_%i" type="standard_car" route="S0_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 18:
                        print('    <vehicle id="W0_L_%i" type="standard_car" route="W0_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 19:
                        print('    <vehicle id="S6_L_%i" type="standard_car" route="S6_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 20:
                        print('    <vehicle id="N6_L_%i" type="standard_car" route="N6_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 21:
                        print('    <vehicle id="E6_L_%i" type="standard_car" route="E6_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 22:
                        print('    <vehicle id="W3_L_%i" type="standard_car" route="W3_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 23:
                        print('    <vehicle id="E3_L_%i" type="standard_car" route="E3_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 24:
                        print('    <vehicle id="N3_L_%i" type="standard_car" route="N3_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 25:
                        print('    <vehicle id="S4_L_%i" type="standard_car" route="S4_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 26:
                        print('    <vehicle id="E4_L_%i" type="standard_car" route="E4_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 27:
                        print('    <vehicle id="W4_L_%i" type="standard_car" route="W4_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 28:
                        print('    <vehicle id="S8_L_%i" type="standard_car" route="S8_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 29:
                        print('    <vehicle id="E8_L_%i" type="standard_car" route="E8_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 30:
                        print('    <vehicle id="W8_L_%i" type="standard_car" route="W8_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    elif route_turn == 31:
                        print('    <vehicle id="S2_L_%i" type="standard_car" route="S2_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
                    else:
                        print('    <vehicle id="N2_L_%i" type="standard_car" route="N2_L" depart="%s" departLane="best"/>' % (car_counter, step), file=routes)
            print("</routes>", file=routes)

