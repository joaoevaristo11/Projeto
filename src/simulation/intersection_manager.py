from src.agents.intersection import Intersection

#INTERSECTIONS NAME
TRAFFIC_LIGHT_NAME_0 = "J0"
TRAFFIC_LIGHT_NAME_1 = "J1"
TRAFFIC_LIGHT_NAME_2 = "J2"
TRAFFIC_LIGHT_NAME_3 = "J3"
TRAFFIC_LIGHT_NAME_4 = "J4"
TRAFFIC_LIGHT_NAME_5 = "J5"
TRAFFIC_LIGHT_NAME_6 = "J6"
TRAFFIC_LIGHT_NAME_7 = "J7"
TRAFFIC_LIGHT_NAME_8 = "J8"

#zonas de espera de pedestres
waiting_zonesTL0 = [":J0_w0", ":J0_w1", ":J0_w2", ":J0_w3"]
waiting_zonesTL1 = [":J1_w0", ":J1_w1", ":J1_w2", ":J1_w3"]
waiting_zonesTL2 = [":J2_w0", ":J2_w1", ":J2_w2", ":J2_w3"]
waiting_zonesTL3 = [":J13_w0", ":J13_w1", ":J13_w2", ":J13_w3"]
waiting_zonesTL4 = [":J9_w0", ":J9_w1", ":J9_w2", ":J9_w3"]
waiting_zonesTL5 = [":J78_w0", ":J78_w1", ":J78_w2", ":J78_w3"]
waiting_zonesTL6 = [":J19_w0", ":J19_w1", ":J19_w2", ":J19_w3"]
waiting_zonesTL7 = [":J17_w0", ":J17_w1", ":J17_w2", ":J17_w3"]
waiting_zonesTL8 = [":J18_w0", ":J18_w1", ":J18_w2", ":J18_w3"]

waiting_zones_lanes_TL0 = [":J0_w0_0", ":J0_w1_0", ":J0_w2_0", ":J0_w3_0"]
waiting_zones_lanes_TL1 = [":J1_w0_0", ":J1_w1_0", ":J1_w2_0", ":J1_w3_0"]
waiting_zones_lanes_TL2 = [":J2_w0_0", ":J2_w1_0", ":J2_w2_0", ":J2_w3_0"]
waiting_zones_lanes_TL3 = [":J13_w0_0", ":J13_w1_0", ":J13_w2_0", ":J13_w3_0"]
waiting_zones_lanes_TL4 = [":J9_w0_0", ":J9_w1_0", ":J9_w2_0", ":J9_w3_0"]
waiting_zones_lanes_TL5 = [":J78_w0_0", ":J78_w1_0", ":J78_w2_0", ":J78_w3_0"]
waiting_zones_lanes_TL6 = [":J19_w0_0", ":J19_w1_0", ":J19_w2_0", ":J19_w3_0"]
waiting_zones_lanes_TL7 = [":J17_w0_0", ":J17_w1_0", ":J17_w2_0", ":J17_w3_0"]
waiting_zones_lanes_TL8 = [":J18_w0_0", ":J18_w1_0", ":J18_w2_0", ":J18_w3_0"]

#lanes of each intersection
route_TL0 = ['N_TL0_1', 'N_TL0_2', 'S_TL0_1', 'S_TL0_2', 'W_TL0_1', 'W_TL0_2', 'TL_TL0_1', 'TL_TL0_2']
route_TL1 = ['TL3_TL_1', 'TL3_TL_2', 'TL4_TL_1', 'TL4_TL_2', 'TL0_TL_1', 'TL0_TL_2', 'TL2_TL_1', 'TL2_TL_2']
route_TL2 = ['N_TL2_1', 'N_TL2_2', 'S_TL2_1', 'S_TL2_2', 'TL_TL2_1', 'TL_TL2_2', 'TL5_TL2_1', 'TL5_TL2_2']
route_TL3 = ['N_TL3_1', 'N_TL3_2', 'TL_TL3_1', 'TL_TL3_2', 'W_TL3_1', 'W_TL3_2', 'E_TL3_1', 'E_TL3_2']
route_TL4 = ['TL_TL4_1', 'TL_TL4_2', 'S_TL4_1', 'S_TL4_2', 'W_TL4_1', 'W_TL4_2', 'E_TL4_1', 'E_TL4_2']
route_TL5 = ['TL7_TL5_1', 'TL7_TL5_2', 'TL8_TL5_1', 'TL8_TL5_2', 'TL2_TL5_1', 'TL2_TL5_2', 'TL6_TL5_1', 'TL6_TL5_2']
route_TL6 = ['N_TL6_1', 'N_TL6_2', 'S_TL6_1', 'S_TL6_2', 'TL5_TL6_1', 'TL5_TL6_2',   'E_TL6_1', 'E_TL6_2']
route_TL7 = ['N_TL7_1', 'N_TL7_2', 'TL5_TL7_1', 'TL5_TL7_2',  'W_TL7_1', 'W_TL7_2', 'E_TL7_1', 'E_TL7_2']
route_TL8 = ['TL5_TL8_1', 'TL5_TL8_2', 'S_TL8_1', 'S_TL8_2', 'W_TL8_1', 'W_TL8_2', 'E_TL8_1', 'E_TL8_2']

roads_200m = ['TL_TL2_1', 'TL_TL2_2', 'TL2_TL_1', 'TL2_TL_2', 'TL_TL3_1', 'TL_TL3_2', 'TL3_TL_1', 'TL3_TL_2',
              'TL5_TL6_1', 'TL5_TL6_2', 'TL6_TL5_1', 'TL6_TL5_2', 'TL5_TL7_1', 'TL5_TL7_2', 'TL7_TL5_1', 'TL7_TL5_2']
roads_400m = ['TL0_TL_1', 'TL0_TL_2', 'TL_TL0_1', 'TL_TL0_2', 'TL_TL4_1', 'TL_TL4_2', 'TL4_TL_1', 'TL4_TL_2',
              'TL2_TL5_1', 'TL2_TL5_2', 'TL5_TL2_1', 'TL5_TL2_2', 'TL5_TL8_1', 'TL5_TL8_2', 'TL8_TL5_1', 'TL8_TL5_2']

def create_intersections(num_states):
    return {
        0: Intersection(TRAFFIC_LIGHT_NAME_0, num_states),
        1: Intersection(TRAFFIC_LIGHT_NAME_1, num_states),
        2: Intersection(TRAFFIC_LIGHT_NAME_2, num_states),
        3: Intersection(TRAFFIC_LIGHT_NAME_3, num_states),
        4: Intersection(TRAFFIC_LIGHT_NAME_4, num_states),
        5: Intersection(TRAFFIC_LIGHT_NAME_5, num_states),
        6: Intersection(TRAFFIC_LIGHT_NAME_6, num_states),
        7: Intersection(TRAFFIC_LIGHT_NAME_7, num_states),
        8: Intersection(TRAFFIC_LIGHT_NAME_8, num_states),
    }

def create_routes():
    return {
        0: route_TL0,
        1: route_TL1,
        2: route_TL2,
        3: route_TL3,
        4: route_TL4,
        5: route_TL5,
        6: route_TL6,
        7: route_TL7,
        8: route_TL8,
    }

def create_waiting_zones():
    return {
        0: [waiting_zonesTL0, waiting_zones_lanes_TL0],
        1: [waiting_zonesTL1, waiting_zones_lanes_TL1],
        2: [waiting_zonesTL2, waiting_zones_lanes_TL2],
        3: [waiting_zonesTL3, waiting_zones_lanes_TL3],
        4: [waiting_zonesTL4, waiting_zones_lanes_TL4],
        5: [waiting_zonesTL5, waiting_zones_lanes_TL5],
        6: [waiting_zonesTL6, waiting_zones_lanes_TL6],
        7: [waiting_zonesTL7, waiting_zones_lanes_TL7],
        8: [waiting_zonesTL8, waiting_zones_lanes_TL8],
    }

def create_tl_names():
    return {
        0: TRAFFIC_LIGHT_NAME_0,
        1: TRAFFIC_LIGHT_NAME_1,
        2: TRAFFIC_LIGHT_NAME_2,
        3: TRAFFIC_LIGHT_NAME_3,
        4: TRAFFIC_LIGHT_NAME_4,
        5: TRAFFIC_LIGHT_NAME_5,
        6: TRAFFIC_LIGHT_NAME_6,
        7: TRAFFIC_LIGHT_NAME_7,
        8: TRAFFIC_LIGHT_NAME_8,
    }

def create_incoming_routes():
    return {
        0: ["N_TL0", "S_TL0", "W_TL0", "TL_TL0"],
        1: ["TL3_TL", "TL4_TL", "TL0_TL", "TL2_TL"],
        2: ["N_TL2", "S_TL2", "TL5_TL2", "TL_TL2"],
        3: ["N_TL3", "TL_TL3", "W_TL3", "E_TL3"],
        4: ["TL_TL4", "S_TL4", "W_TL4", "E_TL4"],
        5: ["TL7_TL5", "TL8_TL5", "TL2_TL5", "TL6_TL5"],
        6: ["TL5_TL6", "N_TL6", "S_TL6", "E_TL6"],
        7: ["TL5_TL7", "N_TL7", "W_TL7", "E_TL7"],
        8: ["TL5_TL8", "S_TL8", "W_TL8", "E_TL8"],
    }

def create_200_400_routes():
    return {
        0: roads_200m,
        1: roads_400m,
    }

def create_map_environment_():
    return {
        0: [0, 1],
        1: [1, 0, 2, 3, 4],
        2: [2, 1, 5],
        3: [3, 1],
        4: [4, 1],
        5: [5, 2, 6, 7, 8],
        6: [6, 5],
        7: [7, 5],
        8: [8, 5],
    }
