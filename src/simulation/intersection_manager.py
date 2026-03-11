from src.agents.intersection import Intersection

# ============================================================================
# IDs DOS SEMÁFOROS NO SUMO
# ============================================================================

TRAFFIC_LIGHT_NAME_1 = "J1"  
TRAFFIC_LIGHT_NAME_2 = "J2"  
TRAFFIC_LIGHT_NAME_3 = "J3"  
TRAFFIC_LIGHT_NAME_4 = "J4"  


# ============================================================================
# ZONAS DE ESPERA DE PEDESTRES - CROSSINGS (Passadeiras)
# ============================================================================
# IDs das travessias/passadeiras onde pedestres atravessam a interseção
# Usados para detetar pedestres em espera para atravessar

waiting_zonesTL1 = [":J1_c0", ":J1_c1", ":J1_c2", ":J1_c3"]  # 4 passadeiras em J1
waiting_zonesTL2 = [":J2_c0", ":J2_c1", ":J2_c2", ":J2_c3"]  # 4 passadeiras em J2
waiting_zonesTL3 = [":J3_c0", ":J3_c1", ":J3_c2", ":J3_c3"]  # 4 passadeiras em J3
waiting_zonesTL4 = [":J4_c0", ":J4_c1", ":J4_c2", ":J4_c3"]  # 4 passadeiras em J4


# ============================================================================
# ZONAS DE ESPERA DE PEDESTRES - WALKING AREAS (Áreas de Espera)
# ============================================================================
# IDs das áreas de espera nos cantos da interseção (antes de atravessar)
# Usados para contar pedestres em espera para entrar na passadeira

waiting_zones_lanes_TL1 = [":J1_w0_0", ":J1_w1_0", ":J1_w2_0", ":J1_w3_0"]  # Cantos de J1
waiting_zones_lanes_TL2 = [":J2_w0_0", ":J2_w1_0", ":J2_w2_0", ":J2_w3_0"]  # Cantos de J2
waiting_zones_lanes_TL3 = [":J3_w0_0", ":J3_w1_0", ":J3_w2_0", ":J3_w3_0"]  # Cantos de J3
waiting_zones_lanes_TL4 = [":J4_w0_0", ":J4_w1_0", ":J4_w2_0", ":J4_w3_0"]  # Cantos de J4


# ============================================================================
# FAIXAS DE TRÁFEGO (LANES) QUE ENTRAM EM CADA INTERSEÇÃO
# ============================================================================
# Lista de todas as LANES (faixas) que chegam a cada interseção
# Usados pelo agente para observar o estado do tráfego (densidade, fila, etc.)


# TL1: Cruzamento Av. Marquês de Tomar com Av. Elias Garcia (Noroeste)
route_TL1 = [
    'MT_NS_1_1',   # Avenida Marquês de Tomar Norte-Sul, segmento 1, faixa 1
    'MT_NS_1_2',   # Avenida Marquês de Tomar Norte-Sul, segmento 1, faixa 2
    'EG_WE_1',     # Avenida Elias Garcia Oeste-Este, segmento 1
    'MT_SN_2_1',   # Avenida Marquês de Tomar Sul-Norte, segmento 2, faixa 1
    'MT_SN_2_2',   # Avenida Marquês de Tomar Sul-Norte, segmento 2, faixa 2
    'EG_EW_2'      # Avenida Elias Garcia Este-Oeste, segmento 2
]

# TL2: Cruzamento Av. 5 de Outubro com Av. Elias Garcia (Nordeste)
route_TL2 = [
    '510_NS_1_1',  # Avenida 5 de Outubro Norte-Sul, segmento 1, faixa 1
    '510_NS_1_2',  # Avenida 5 de Outubro Norte-Sul, segmento 1, faixa 2
    'EG_EW_1',     # Avenida Elias Garcia Este-Oeste, segmento 1
    'EG_WE_2',     # Avenida Elias Garcia Oeste-Este, segmento 2
    '510_SN_2_1',  # Avenida 5 de Outubro Sul-Norte, segmento 2, faixa 1
    '510_SN_2_2'   # Avenida 5 de Outubro Sul-Norte, segmento 2, faixa 2
]

# TL3: Cruzamento Av. 5 de Outubro com Av. Visconde de Valmor (Sudeste)
route_TL3 = [
    '510_NS_2_1',  # Avenida 5 de Outubro Norte-Sul, segmento 2, faixa 1
    '510_NS_2_2',  # Avenida 5 de Outubro Norte-Sul, segmento 2, faixa 2
    'VV_EW_1',     # Avenida Visconde de Valmor Este-Oeste, segmento 1
    'VV_WE_2',     # Avenida Visconde de Valmor Oeste-Este, segmento 2
    '510_SN_1_1',  # Avenida 5 de Outubro Sul-Norte, segmento 1, faixa 1
    '510_SN_1_2'   # Avenida 5 de Outubro Sul-Norte, segmento 1, faixa 2
]

# TL4: Cruzamento Av. Marquês de Tomar com Av. Visconde de Valmor (Sudoeste)
route_TL4 = [
    'MT_NS_2_1',   # Avenida Marquês de Tomar Norte-Sul, segmento 2, faixa 1
    'MT_NS_2_2',   # Avenida Marquês de Tomar Norte-Sul, segmento 2, faixa 2
    'VV_WE_1',     # Avenida Visconde de Valmor Oeste-Este, segmento 1
    'VV_EW_2',     # Avenida Visconde de Valmor Este-Oeste, segmento 2
    'MT_SN_1_1',   # Avenida Marquês de Tomar Sul-Norte, segmento 1, faixa 1
    'MT_SN_1_2'    # Avenida Marquês de Tomar Sul-Norte, segmento 1, faixa 2
]

# ============================================================================
# CLASSIFICAÇÃO DE ESTRADAS POR COMPRIMENTO 
# ============================================================================
# Código antigo para classificar estradas por comprimento (110m vs 132m)
# Usado pelo módulo SAPA para ajustar tempos de verde dinamicamente

roads_110m = ['MT_SN_2_1', 
              'MT_SN_2_2', 
              'MT_NS_2_1', 
              'MT_NS_2_2', 
              '510_NS_2_1', 
              '510_NS_2_2', 
              '510_SN_2_1',
              '510_SN_2_2'
              ]  # Estradas curtas
roads_132m = ['EG_EW_2',
              'EG_WE_2',
              'VV_EW_2',
              'VV_WE_2']  # Estradas longas



# ============================================================================
# FUNÇÕES DE INICIALIZAÇÃO
# ============================================================================

def create_intersections(num_states):
    #Cria objetos Intersection para cada semáforo da rede.
    
    return {
        1: Intersection(TRAFFIC_LIGHT_NAME_1, num_states),  # Agente C1 controla J1
        2: Intersection(TRAFFIC_LIGHT_NAME_2, num_states),  # Agente C2 controla J2
        3: Intersection(TRAFFIC_LIGHT_NAME_3, num_states),  # Agente C3 controla J3
        4: Intersection(TRAFFIC_LIGHT_NAME_4, num_states),  # Agente C4 controla J4
    }


def create_routes():
    #Retorna as faixas (lanes) de entrada para cada interseção.

    return {
        1: route_TL1,  # 6 faixas que chegam a J1
        2: route_TL2,  # 6 faixas que chegam a J2
        3: route_TL3,  # 6 faixas que chegam a J3
        4: route_TL4,  # 6 faixas que chegam a J4
    }


def create_waiting_zones():
    #Retorna as zonas de espera de pedestres para cada interseção.
    
    return {
        1: [waiting_zonesTL1, waiting_zones_lanes_TL1],  # Zonas de pedestres J1
        2: [waiting_zonesTL2, waiting_zones_lanes_TL2],  # Zonas de pedestres J2
        3: [waiting_zonesTL3, waiting_zones_lanes_TL3],  # Zonas de pedestres J3
        4: [waiting_zonesTL4, waiting_zones_lanes_TL4],  # Zonas de pedestres J4
    }


def create_tl_names():
    #Retorna o ID SUMO de cada semáforo.
    
    return {
        1: TRAFFIC_LIGHT_NAME_1,  # "J1"
        2: TRAFFIC_LIGHT_NAME_2,  # "J2"
        3: TRAFFIC_LIGHT_NAME_3,  # "J3"
        4: TRAFFIC_LIGHT_NAME_4,  # "J4"
    }

def create_incoming_routes():
   
    #Retorna os edges (estradas, sem número de faixa) que chegam a cada interseção.
    
    return {
        1: ["MT_NS_1", "EG_WE_2", "EG_WE_1", "MT_SN_2"],      # J1: 4 edges de entrada
        2: ["510_NS_1", "EG_EW_1", "EG_WE_2", "510_SN_2"],    # J2: 4 edges de entrada
        3: ["510_NS_2", "VV_EW_1", "VV_WE_2", "510_SN_1"],    # J3: 4 edges de entrada
        4: ["MT_NS_2", "VV_WE_2", "VV_EW_1", "MT_SN_1"],      # J4: 4 edges de entrada
    }


def create_110_132_routes():
    """
    Classifica estradas por comprimento para ajuste adaptativo SAPA.
    
    O módulo SAPA usa esta informação para ajustar dinamicamente os tempos
    de verde dos semáforos baseado na distância que os veículos têm de percorrer:
    - Estradas curtas (110m): menos tempo para veículos chegarem
    - Estradas longas (132m): mais tempo para veículos chegarem
    """
    return {
        0: roads_110m,  # Estradas curtas (110m)
        1: roads_132m,  # Estradas longas (132m)
    }


def create_map_environment_():
    #Define a topologia da rede: quais interseções estão conectadas entre si.
    return {
        1: [1, 2, 3],  # J1 ligado a J2 (Este) e J3 (Sul)
        2: [2, 1, 4],  # J2 ligado a J1 (Oeste) e J4 (Sul)
        3: [3, 1, 4],  # J3 ligado a J1 (Norte) e J4 (Este)
        4: [4, 2, 3],  # J4 ligado a J2 (Norte) e J3 (Oeste)
    }
