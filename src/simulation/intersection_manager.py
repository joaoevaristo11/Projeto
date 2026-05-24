from src.agents.intersection import Intersection

# ============================================================================
# IDs DOS SEMÁFOROS NO SUMO
# ============================================================================

TRAFFIC_LIGHT_NAME_1 = "J1"  # Cruzamento Av. Marquês de Tomar x Av. Elias Garcia    (Noroeste)
TRAFFIC_LIGHT_NAME_2 = "J2"  # Cruzamento Av. 5 de Outubro   x Av. Elias Garcia    (Nordeste)
TRAFFIC_LIGHT_NAME_3 = "J3"  # Cruzamento Av. Marquês de Tomar x Av. Visconde de Valmor (Sudoeste)
TRAFFIC_LIGHT_NAME_4 = "J4"  # Cruzamento Av. 5 de Outubro   x Av. Visconde de Valmor (Sudeste)

# ============================================================================
# ZONAS DE ESPERA DE PEDESTRES - CROSSINGS (Passadeiras)
# ============================================================================

waiting_zonesTL1 = [":J1_c0", ":J1_c1", ":J1_c2", ":J1_c3"]
waiting_zonesTL2 = [":J2_c0", ":J2_c1", ":J2_c2", ":J2_c3"]
waiting_zonesTL3 = [":J3_c0", ":J3_c1", ":J3_c2", ":J3_c3"]
waiting_zonesTL4 = [":J4_c0", ":J4_c1", ":J4_c2", ":J4_c3"]

# ============================================================================
# ZONAS DE ESPERA DE PEDESTRES - WALKING AREAS
# ============================================================================

waiting_zones_lanes_TL1 = [":J1_w0_0", ":J1_w1_0", ":J1_w2_0", ":J1_w3_0"]
waiting_zones_lanes_TL2 = [":J2_w0_0", ":J2_w1_0", ":J2_w2_0", ":J2_w3_0"]
waiting_zones_lanes_TL3 = [":J3_w0_0", ":J3_w1_0", ":J3_w2_0", ":J3_w3_0"]
waiting_zones_lanes_TL4 = [":J4_w0_0", ":J4_w1_0", ":J4_w2_0", ":J4_w3_0"]

# ============================================================================
# FAIXAS DE TRÁFEGO (LANES) QUE ENTRAM EM CADA INTERSEÇÃO
# ============================================================================

route_TL1 = [
    'MT_NS_1',   # Av. Marquês de Tomar Norte→Sul, segmento 1 (externo Norte)
    'EG_WE_1',   # Av. Elias Garcia Oeste→Este, segmento 1 (externo Oeste)
    'MT_SN_2',   # Av. Marquês de Tomar Sul→Norte, segmento 2 (vem de J3)
    'EG_EW_2',   # Av. Elias Garcia Este→Oeste, segmento 2 (vem de J2)
]

route_TL2 = [
    '510_NS_1',  # Av. 5 de Outubro Norte→Sul, segmento 1 (externo Norte, 3 lanes)
    'EG_WE_2',   # Av. Elias Garcia Oeste→Este, segmento 2 (vem de J1, 2 lanes)
    '510_SN_2',  # Av. 5 de Outubro Sul→Norte, segmento 2 (vem de J4, 3 lanes)
    'EG_EW_1',   # Av. Elias Garcia Este→Oeste, segmento 1 (externo Este, 2 lanes)
]

route_TL3 = [
    'MT_NS_2',   # Av. Marquês de Tomar Norte→Sul, segmento 2 (vem de J1)
    'VV_WE_1',   # Av. Visconde de Valmor Oeste→Este, segmento 1 (externo Oeste)
    'MT_SN_1',   # Av. Marquês de Tomar Sul→Norte, segmento 1 (externo Sul)
    'VV_EW_2',   # Av. Visconde de Valmor Este→Oeste, segmento 2 (vem de J4)
]

route_TL4 = [
    '510_NS_2',  # Av. 5 de Outubro Norte→Sul, segmento 2 (vem de J2, 3 lanes)
    'VV_WE_2',   # Av. Visconde de Valmor Oeste→Este, segmento 2 (vem de J3, 2 lanes)
    '510_SN_1',  # Av. 5 de Outubro Sul→Norte, segmento 1 (externo Sul, 3 lanes)
    'VV_EW_1',   # Av. Visconde de Valmor Este→Oeste, segmento 1 (externo Este, 2 lanes)
]

# ============================================================================
# CLASSIFICAÇÃO DE ESTRADAS POR COMPRIMENTO
# ============================================================================

roads_110m = [
    'MT_NS_1', 'MT_NS_2', 'MT_NS_3',
    'MT_SN_1', 'MT_SN_2', 'MT_SN_3',
    '510_NS_1', '510_NS_2', '510_NS_3',
    '510_SN_1', '510_SN_2', '510_SN_3',
]

roads_132m = [
    'EG_EW_1', 'EG_EW_2', 'EG_EW_3',
    'EG_WE_1', 'EG_WE_2', 'EG_WE_3',
    'VV_EW_1', 'VV_EW_2', 'VV_EW_3',
    'VV_WE_1', 'VV_WE_2', 'VV_WE_3',
]

# ============================================================================
# FUNÇÕES DE INICIALIZAÇÃO
# ============================================================================

def create_intersections(num_states):
    """
    Cria objetos Intersection para cada semáforo da rede.

    ALTERADO: num_states pode ser:
      - int:  mesmo valor para todos os cruzamentos (retrocompatível)
      - dict: {idx: num_states} com valor específico por cruzamento
              ex: {1: 170, 2: 176, 3: 170, 4: 176}
    """
    # ADICIONADO: suporte a dict para num_states diferente por cruzamento
    def _ns(idx):
        if isinstance(num_states, dict):
            return num_states[idx]
        return num_states

    return {
        1: Intersection(TRAFFIC_LIGHT_NAME_1, _ns(1)),  # J1 → Cell_1 → 170
        2: Intersection(TRAFFIC_LIGHT_NAME_2, _ns(2)),  # J2 → Cell_2 → 176
        3: Intersection(TRAFFIC_LIGHT_NAME_3, _ns(3)),  # J3 → Cell_1 → 170
        4: Intersection(TRAFFIC_LIGHT_NAME_4, _ns(4)),  # J4 → Cell_2 → 176
    }


def create_routes():
    """Retorna as faixas (lanes) de entrada para cada interseção em ordem N, O, S, E."""
    return {
        1: route_TL1,  # 4 edges, todos com 2 lanes (MT_* e EG_*)
        2: route_TL2,  # 4 edges: 510_* com 3 lanes, EG_* com 2 lanes
        3: route_TL3,  # 4 edges, todos com 2 lanes (MT_* e VV_*)
        4: route_TL4,  # 4 edges: 510_* com 3 lanes, VV_* com 2 lanes
    }


def create_waiting_zones():
    """Retorna as zonas de espera de pedestres para cada interseção."""
    return {
        1: [waiting_zonesTL1, waiting_zones_lanes_TL1],
        2: [waiting_zonesTL2, waiting_zones_lanes_TL2],
        3: [waiting_zonesTL3, waiting_zones_lanes_TL3],
        4: [waiting_zonesTL4, waiting_zones_lanes_TL4],
    }


def create_tl_names():
    """Retorna o ID SUMO de cada semáforo."""
    return {
        1: TRAFFIC_LIGHT_NAME_1,  # "J1"
        2: TRAFFIC_LIGHT_NAME_2,  # "J2"
        3: TRAFFIC_LIGHT_NAME_3,  # "J3"
        4: TRAFFIC_LIGHT_NAME_4,  # "J4"
    }


def create_incoming_routes():
    """Retorna os edges que chegam a cada interseção em ordem N, O, S, E."""
    return {
        1: ["MT_NS_1", "EG_WE_1", "MT_SN_2", "EG_EW_2"],
        2: ["510_NS_1", "EG_WE_2", "510_SN_2", "EG_EW_1"],
        3: ["MT_NS_2", "VV_WE_1", "MT_SN_1", "VV_EW_2"],
        4: ["510_NS_2", "VV_WE_2", "510_SN_1", "VV_EW_1"],
    }


def create_110_132_routes():
    """
    Classifica estradas por comprimento.
    - roads_110m: Av. Marquês de Tomar e Av. 5 de Outubro (eixo vertical)
    - roads_132m: Av. Elias Garcia e Av. Visconde de Valmor (eixo horizontal)
    """
    return {
        0: roads_110m,
        1: roads_132m,
    }


def create_map_environment_():
    """Define a topologia da rede: quais interseções estão conectadas entre si."""
    return {
        1: [1, 2, 3],
        2: [2, 1, 4],
        3: [3, 1, 4],
        4: [4, 2, 3],
    }