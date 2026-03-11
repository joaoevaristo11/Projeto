import numpy as np
import math
#from scipy.stats import truncnorm
import matplotlib.pyplot as plt
import pandas as pd

class PedestrianGenerator:
    def __init__(self, max_steps, n_ped_generated):
        self._n_ped_generated = n_ped_generated  # how many pedestrians per episode
        self._max_steps = max_steps

    def generate_ped_routefile(self, seed):
        """
        Generation of the route of every pedestrian for one episode
        """
        np.random.seed(seed)  # make tests reproducible

        # the generation of pedestrians is distributed according to a weibull distribution
        #alpha = 2
        timings = np.random.weibull(4, self._n_ped_generated)
        # Normalizar os valores para o intervalo [0, 1]
        timings = timings - np.min(timings)  # Garante que o mínimo seja 0
        timings = timings / np.max(timings)  # Garante que o máximo seja 1
        timings = timings * self._max_steps
        timings = np.sort(timings)
        ped_gen_steps = np.rint(timings)  # round every value to int -> effective steps when a pedestrian will be generated


        # produce the file for cars generation, one car per line
        with open("sumo/pedestrian_routes.rou.xml", "w") as routes:
            print("""<routes>
            <vType vClass ="pedestrian" id="standard_ped" maxSpeed="0.90" />'
            
            <route id="N0_S0_" edges="N_TL0 TL0_S"/>
            <route id="S0_N0_" edges="S_TL0 TL0_N"/>
            <route id="TLs0_N0" edges="TL0_S N_TL0"/>
            <route id="TLn0_S0" edges="TL0_N S_TL0"/>
            
            <route id="N6_S6_" edges="N_TL6 TL6_S"/>
            <route id="S6_N6_" edges="S_TL6 TL6_N"/>
            <route id="TLs6_N6" edges="TL6_S N_TL6"/>
            <route id="TLn6_S6" edges="TL6_N S_TL6"/>
            
            <route id ="N3_S4_" edges ="N_TL3 TL3_TL TL_TL4 TL4_S"/>
            <route id ="TLn3_S4" edges ="TL3_N TL_TL3 TL4_TL E_TL4"/>
            
            <route id ="N7_S8_" edges ="N_TL7 TL7_TL5 TL5_TL8 TL8_S"/>
            <route id ="TLn7_S8" edges ="TL7_N TL5_TL7 TL8_TL5 E_TL8"/>
            
            <route id ="S8_N7_" edges ="S_TL8 TL8_TL5 TL5_TL7 TL7_N"/>
            <route id ="TLs8_N7" edges ="TL8_S TL5_TL8 TL7_TL5 N_TL7"/>
            
            <route id ="W4_E4_" edges = "W_TL4 TL4_E"/>
            <route id ="E4_W4_" edges = "E_TL4 TL4_W"/>
            
            <route id="S0_S4_" edges="S_TL0 TL0_TL TL_TL4 TL4_S"/>
            <route id="E3_N2_" edges="TL3_E TL_TL3 TL2_TL N_TL2"/>
            <route id="W3_N0_" edges="W_TL3 TL3_TL TL_TL0 TL0_N"/>
            <route id="N2_S2_" edges="N_TL2 TL2_S "/>
            <route id="TL2s_N2" edges="TL2_S N_TL2"/>
            <route id="TL2s_W" edges="TL2_S TL_TL2 TL0_TL S_TL0"/>
            <route id="TL2n_S" edges="TL2_N S_TL2"/>
            <route id="TL2n_E" edges="TL2_N TL5_TL2 TL7_TL5 N_TL7"/>
            <route id="TL2n_E2" edges="TL2_N TL2_TL5 TL5_TL6 TL6_E"/>
            <route id="S2_N0_" edges="S_TL2 TL_TL2 TL0_TL TL0_N"/>""", file=routes)


            for ped_counter, step in enumerate(ped_gen_steps):

                route_straight = np.random.randint(1, 25)  # choose a random source & destination
                    #pedestres a circular em C0
                if route_straight == 1:
                    print('<person id="N0_S0_%i"  depart="%s" departPos="3" >'
                          '     <walk route ="N0_S0_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 2:
                    print('<person id="S0_N0_%i"  depart="%s" departPos="3" >'
                          '     <walk route ="S0_N0_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 3:
                    print('<person id="TLn0_S0_%i"  depart="%s" departPos="100"  >'
                          '     <walk route ="TLn0_S0"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 4:
                    print('<person id="TLs0_N0_%i"  depart="%s" departPos="100"  >'
                          '     <walk route ="TLs0_N0"/>'
                          '</person>' % (ped_counter, step), file=routes)
                # pedestres a circular em C3
                elif route_straight == 5:
                    print('<person id="N3_S4_%i"  depart="%s" departPos="3" >'
                          '     <walk route ="N3_S4_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 7:
                    print('<person id="TLn3_S4_%i"  depart="%s" departPos="100" >'
                          '     <walk route ="TLn3_S4"/>'
                          '</person>' % (ped_counter, step), file=routes)
                # pedestres a circular em c2
                elif route_straight == 8:
                    print('<person id="TL2n_S_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TL2n_S"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 9:
                    print('<person id="TL2s_N2_%i"  depart="%s" departPos="100" >'
                          '     <walk route ="TL2s_N2"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 10:
                    print('<person id="N2_S2_%i"  depart="%s" departPos="3">'
                          '     <walk route ="N2_S2_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                #pedestres a circular em c4
                elif route_straight == 11:
                    print('<person id="W4_E4_%i"  depart="%s" departPos="3" >'
                          '     <walk route ="W4_E4_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 12:
                    print('<person id="E4_W4_%i"  depart="%s" departPos="3" >'
                          '     <walk route ="E4_W4_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 13:
                    print('<person id="E3_N2_%i"  depart="%s" departPos="100" >'
                          '     <walk route ="E3_N2_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 14:
                    print('<person id="W3_N0_%i"  depart="%s" departPos="3">'
                          '     <walk route ="W3_N0_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                # Norte TL1 e Norte TL2
                elif route_straight == 15:
                    print('<person id="TL2n_E_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TL2n_E"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 16:
                    print('<person id="TL2n_E2_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TL2n_E2"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 17:
                    print('<person id="TLs8_N7_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TLs8_N7"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 18:
                    print('<person id="S8_N7_%i"  depart="%s" departPos="100">'
                          '     <walk route ="S8_N7_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 19:
                    print('<person id="N7_S8_%i"  depart="%s" departPos="100">'
                          '     <walk route ="N7_S8_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 20:
                    print('<person id="TLn7_S8_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TLn7_S8"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 21:
                    print('<person id="N6_S6_%i"  depart="%s" departPos="100">'
                          '     <walk route ="N6_S6_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 22:
                    print('<person id="S6_N6_%i"  depart="%s" departPos="100">'
                          '     <walk route ="S6_N6_"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 23:
                    print('<person id="TLs6_N6_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TLs6_N6"/>'
                          '</person>' % (ped_counter, step), file=routes)
                elif route_straight == 24:
                    print('<person id="TLn6_S6_%i"  depart="%s" departPos="100">'
                          '     <walk route ="TLn6_S6"/>'
                          '</person>' % (ped_counter, step), file=routes)
            print("</routes>", file=routes)
