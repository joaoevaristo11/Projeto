import numpy as np
import math


class PedestrianGenerator:
    def __init__(self, max_steps, n_ped_generated):
        self._n_ped_generated = n_ped_generated  # how many pedestrians per episode
        self._max_steps = max_steps

    def generate_ped_routefile(self, seed):
        """
        Generation of the route of every pedestrian for one episode.

        Distribuicao por cruzamento calibrada com dados reais de campo (hora de ponta):
          C1 (J1): 700 ped/h  25.8%
          C2 (J2): 852 ped/h  31.4%
          C3 (J3): 640 ped/h  23.6%
          C4 (J4): 520 ped/h  19.2%
          Total  : 2712 ped/h 100%

        Dentro de cada cruzamento, as 4 rotas sao equiprovaveis (25% cada).
        """
        np.random.seed(seed)  # make tests reproducible

        # the generation of pedestrians is distributed according to a weibull distribution
        timings = np.random.weibull(4, self._n_ped_generated)
        # Normalizar os valores para o intervalo [0, 1]
        timings = timings - np.min(timings)
        timings = timings / np.max(timings)
        timings = timings * self._max_steps
        timings = np.sort(timings)
        ped_gen_steps = np.rint(timings)  # round every value to int -> effective steps when a pedestrian will be generated

        # Probabilidades por cruzamento: C1=700, C2=852, C3=640, C4=520 ped/h, total=2712
        P_J1 = 700 / 2712   # 0.258
        P_J2 = 852 / 2712   # 0.314
        P_J3 = 640 / 2712   # 0.236
        # P_J4 = restante    # 0.192

        with open("sumo/pedestrian_routes.rou.xml", "w", encoding="utf-8") as routes:
            print("""<routes>
    <vType id="standard_ped" vClass="pedestrian" maxSpeed="1.2" minGap="0.25" width="0.5"/>

    <!-- J1: Av. Marques de Tomar x Av. Elias Garcia (Noroeste) 700 ped/h -->
    <route id="J1_EG_W_MT_S" edges="EG_WE_1 :J1_w2 :J1_c1 MT_NS_2"/>
    <route id="J1_MT_N_EG_E" edges="MT_NS_1 :J1_w3 :J1_c2 EG_EW_3"/>
    <route id="J1_EG_E_MT_N" edges="EG_EW_2 :J1_w0 :J1_c3 MT_SN_3"/>
    <route id="J1_MT_S_EG_W" edges="MT_SN_2 :J1_w1 :J1_c0 EG_WE_2"/>

    <!-- J2: Av. 5 de Outubro x Av. Elias Garcia (Nordeste) 852 ped/h -->
    <route id="J2_EG_W_510_S" edges="EG_WE_2 :J2_w2 :J2_c1 510_NS_2"/>
    <route id="J2_510_N_EG_E" edges="510_NS_1 :J2_w3 :J2_c2 EG_EW_2"/>
    <route id="J2_EG_E_510_N" edges="EG_EW_1 :J2_w0 :J2_c3 510_SN_3"/>
    <route id="J2_510_S_EG_W" edges="510_SN_2 :J2_w1 :J2_c0 EG_WE_3"/>

    <!-- J3: Av. Marques de Tomar x Av. Visconde de Valmor (Sudoeste) 640 ped/h -->
    <route id="J3_VV_W_MT_S" edges="VV_WE_1 :J3_w2 :J3_c1 MT_NS_3"/>
    <route id="J3_MT_N_VV_E" edges="MT_NS_2 :J3_w3 :J3_c2 VV_EW_3"/>
    <route id="J3_VV_E_MT_N" edges="VV_EW_2 :J3_w0 :J3_c3 MT_SN_2"/>
    <route id="J3_MT_S_VV_W" edges="MT_SN_1 :J3_w1 :J3_c0 VV_WE_2"/>

    <!-- J4: Av. 5 de Outubro x Av. Visconde de Valmor (Sudeste) 520 ped/h -->
    <route id="J4_VV_W_510_S" edges="VV_WE_2 :J4_w2 :J4_c1 510_NS_3"/>
    <route id="J4_510_N_VV_E" edges="510_NS_2 :J4_w3 :J4_c2 VV_EW_2"/>
    <route id="J4_VV_E_510_N" edges="VV_EW_1 :J4_w0 :J4_c3 510_SN_2"/>
    <route id="J4_510_S_VV_W" edges="510_SN_1 :J4_w1 :J4_c0 VV_WE_3"/>
""", file=routes)

            for ped_counter, step in enumerate(ped_gen_steps):

                # Escolha do cruzamento com probabilidades calibradas pelos dados reais
                intersection_choice = np.random.uniform()
                # Escolha da rota dentro do cruzamento (4 rotas equiprovaveis)
                route_within = np.random.randint(1, 5)  # 1, 2, 3 ou 4

                if intersection_choice < P_J1:
                    # J1: Marques de Tomar x Elias Garcia (25.8%)
                    if route_within == 1:
                        print('<person id="J1_EG_W_MT_S_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J1_EG_W_MT_S"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 2:
                        print('<person id="J1_MT_N_EG_E_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J1_MT_N_EG_E"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 3:
                        print('<person id="J1_EG_E_MT_N_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J1_EG_E_MT_N"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 4:
                        print('<person id="J1_MT_S_EG_W_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J1_MT_S_EG_W"/>'
                              '</person>' % (ped_counter, step), file=routes)

                elif intersection_choice < P_J1 + P_J2:
                    # J2: 5 de Outubro x Elias Garcia (31.4%)
                    if route_within == 1:
                        print('<person id="J2_EG_W_510_S_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J2_EG_W_510_S"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 2:
                        print('<person id="J2_510_N_EG_E_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J2_510_N_EG_E"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 3:
                        print('<person id="J2_EG_E_510_N_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J2_EG_E_510_N"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 4:
                        print('<person id="J2_510_S_EG_W_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J2_510_S_EG_W"/>'
                              '</person>' % (ped_counter, step), file=routes)

                elif intersection_choice < P_J1 + P_J2 + P_J3:
                    # J3: Marques de Tomar x Visconde de Valmor (23.6%)
                    if route_within == 1:
                        print('<person id="J3_VV_W_MT_S_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J3_VV_W_MT_S"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 2:
                        print('<person id="J3_MT_N_VV_E_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J3_MT_N_VV_E"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 3:
                        print('<person id="J3_VV_E_MT_N_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J3_VV_E_MT_N"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 4:
                        print('<person id="J3_MT_S_VV_W_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J3_MT_S_VV_W"/>'
                              '</person>' % (ped_counter, step), file=routes)

                else:
                    # J4: 5 de Outubro x Visconde de Valmor (19.2%)
                    if route_within == 1:
                        print('<person id="J4_VV_W_510_S_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J4_VV_W_510_S"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 2:
                        print('<person id="J4_510_N_VV_E_%i" type="standard_ped" depart="%s" departPos="3">'
                              '    <walk route="J4_510_N_VV_E"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 3:
                        print('<person id="J4_VV_E_510_N_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J4_VV_E_510_N"/>'
                              '</person>' % (ped_counter, step), file=routes)
                    elif route_within == 4:
                        print('<person id="J4_510_S_VV_W_%i" type="standard_ped" depart="%s" departPos="100">'
                              '    <walk route="J4_510_S_VV_W"/>'
                              '</person>' % (ped_counter, step), file=routes)

            print("</routes>", file=routes)