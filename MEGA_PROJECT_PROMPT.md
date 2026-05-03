# 🚦 MEGA PROJETO: Sistema Multi-Agente de Controlo de Tráfego com DDQN

## 📌 RESUMO EXECUTIVO

**Projeto:** Sistema Inteligente de Gestão de Tráfego Urbano em Tempo Real
**Objetivo Principal:** Controlar 4 interseções urbanas de forma coordenada usando Deep Q-Learning (DDQN) para minimizar tempos de espera de veículos e pedestres
**Paradigma:** Reinforcement Learning + Simulação em Tempo Real (SUMO) + Redes Neurais Profundas (TensorFlow)
**Escopo:** 2 modelos neurais partilhados por 4 agentes (2 agentes por modelo)

---

## 🎯 OBJETIVOS E ESCOPO

### Problemas que o Projeto Resolve
1. **Congestão de Tráfego**: Redução de tempos de espera em interseções urbanas
2. **Gestão Adaptativa**: Ajuste dinâmico de fases dos semáforos conforme tráfego em tempo real
3. **Coordenação Multi-Agente**: Colaboração entre múltiplos controladores sem comunicação centralizada
4. **Suporte a Pedestres**: Considerar tempos de travessia de pedestres nas decisões

### Abordagem Técnica
- **Deep Double Q-Network (DDQN)**: Algoritmo de RL com duas redes (main + target) para melhorar estabilidade
- **Experience Replay**: Buffer de memória para treino eficiente com experiências passadas
- **SAPA Module**: Ajuste adaptativo da duração de fases verdes baseado em fila de veículos
- **Multi-modelo**: 2 modelos independentes para 2 "células" de cruzamentos

---

## 🏗️ ARQUITETURA GERAL DO SISTEMA

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SIMULADOR SUMO (Ambiente)                        │
│              (Simulation of Urban MObility - TraCI API)             │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ TraCI (Python↔SUMO em tempo real)
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
    ┌───▼─────┐                       ┌───▼──────┐
    │ Célula 1 │                       │ Célula 2 │
    │ J1 + J3  │                       │ J2 + J4  │
    └───┬─────┘                       └───┬──────┘
        │                                 │
        │                                 │
    ┌───▼──────────────┐         ┌────────▼──────────┐
    │ Model_Cell_1     │         │ Model_Cell_2      │
    │ (DDQN Network)   │         │ (DDQN Network)    │
    │ Input: 172 dims  │         │ Input: 172 dims   │
    │ Output: 8 ações  │         │ Output: 8 ações   │
    │ TensorFlow/Keras │         │ TensorFlow/Keras  │
    └────────────────┬─┘         └────────────┬───────┘
                     │                        │
        ┌────────────┴────────┬───────────────┴────────┐
        │                     │                        │
    ┌───▼──────┐         ┌────▼─────┐            ┌────▼─────┐
    │ Memory_1  │         │ J1 Agent │            │ J2 Agent │
    │ Replay    │         │ (Action) │            │ (Action) │
    │ Buffer    │         └──────────┘            └──────────┘
    └───┬──────┘
        │                 ┌──────────┐            ┌──────────┐
        │                 │ J3 Agent │            │ J4 Agent │
        │                 │ (Action) │            │ (Action) │
    ┌───▼──────┐         └──────────┘            └──────────┘
    │ Memory_2  │
    │ Replay    │
    │ Buffer    │
    └───────────┘
```

### Componentes Principais

| Componente | Função | Localização |
|-----------|--------|------------|
| **SUMO Simulator** | Simula tráfego urbano realista | Externo (SUMO/sumo_config.sumocfg) |
| **TraCI API** | Bridge Python ↔ SUMO | Integrado via `traci` |
| **DDQN Models** | Redes neurais para decisões | `src/agents/model.py` |
| **Experience Replay** | Buffer de memória (s,a,r,s',done) | `src/agents/memory.py` |
| **Intersection Manager** | Orquestra 4 cruzamentos | `src/simulation/intersection_manager.py` |
| **SAPA Module** | Ajuste adaptativo de fases | `src/algorithms/sapa.py` |
| **Training Loop** | Ciclo treino com epsilon-decay | `src/simulation/training_simulation.py` |
| **Testing Loop** | Avaliação de modelos | `src/simulation/testing_simulation.py` |
| **Visualization** | Plots e análise de métricas | `src/utils/visualization.py` |

---

## 📂 ESTRUTURA COMPLETA DE PASTAS E FICHEIROS

```
Projeto/
│
├── 📄 README.md                          [Documentação principal]
├── 📄 requirements.txt                   [Dependências Python]
├── 📄 training_main.py                   [Script principal de TREINO]
├── 📄 testing_main.py                    [Script principal de TESTE]
├── 📄 MEGA_PROJECT_PROMPT.md             [ESTE FICHEIRO - Documentação completa]
│
├── 📂 src/                               [CÓDIGO-FONTE PRINCIPAL]
│   │
│   ├── 📂 agents/                        [Componentes de Aprendizagem]
│   │   ├── model.py                      [DDQN Network (Train + Test Models)]
│   │   │   └── TrainModel class:         Rede principal + target (treino)
│   │   │   └── TestModel class:          Rede para inferência
│   │   │   └── Métodos: predict, train_batch, copy_weights, save/load
│   │   │
│   │   ├── memory.py                     [Experience Replay Buffer]
│   │   │   └── Memory class:             Armazena (s,a,r,s',done)
│   │   │   └── Métodos: add_sample, get_samples, _size_now
│   │   │   └── Configurable: size_max, size_min
│   │   │
│   │   └── intersection.py               [LÓGICA DE ESTADO/AÇÃO POR CRUZAMENTO]
│   │       └── Intersection class:       Representa 1 cruzamento
│   │       └── Atributos de estado:      reward_episode, cumulative_wait, queue_length
│   │       └── Métodos principais:
│   │           - get_state():            Extrai 172-dim state vector
│   │           - choose_phase():         Escolhe verde ou amarelo
│   │           - pedestrians_state():    Incorpora estado de pedestres
│   │           - lane_occupancy():       Adiciona ocupação de faixas
│   │           - action_encode():        Codifica ação em 8 dimensões
│   │           - collect_waiting_times(): Calcula tempos de espera
│   │
│   ├── 📂 simulation/                    [LOOPS DE SIMULAÇÃO]
│   │   │
│   │   ├── training_simulation.py        [LOOP DE TREINO]
│   │   │   └── Simulation class (treino)
│   │   │   └── Métodos: run(episode, epsilon, episode_seed)
│   │   │   └── Executa:
│   │   │       1. Gera tráfego (veículos + pedestres)
│   │   │       2. Agentes observam estado
│   │   │       3. DDQN prediz ações com epsilon-greedy
│   │   │       4. Executa ações no SUMO
│   │   │       5. Coleta recompensas
│   │   │       6. Armazena em Experience Replay
│   │   │       7. Treina redes com mini-batches
│   │   │
│   │   ├── testing_simulation.py         [LOOP DE TESTE]
│   │   │   └── Simulation class (teste)
│   │   │   └── Métodos: run(episode_seed)
│   │   │   └── Modos: 'SUMO' (modelos), 'REAL'/'BASELINE'/'FIXED' (sem IA)
│   │   │   └── Coleta métricas:
│   │   │       - Queue length por cruzamento
│   │   │       - Pedestrian halting times
│   │   │       - Average phase duration
│   │   │       - Average waiting times (veículos)
│   │   │       - Average speed em zonas verdes
│   │   │       - Lane volume por avenida
│   │   │
│   │   ├── intersection_manager.py       [ORQUESTRAÇÃO DE CRUZAMENTOS]
│   │   │   └── TRAFFIC_LIGHT_NAMES:
│   │   │       J1: Av. Marquês de Tomar × Av. Elias Garcia (Noroeste)
│   │   │       J2: Av. 5 de Outubro × Av. Elias Garcia (Nordeste)
│   │   │       J3: Av. Marquês de Tomar × Av. Visconde de Valmor (Sudoeste)
│   │   │       J4: Av. 5 de Outubro × Av. Visconde de Valmor (Sudeste)
│   │   │   │
│   │   │   └── Routes (4 edges por cruzamento):
│   │   │       route_TL1: [MT_NS_1, EG_WE_1, MT_SN_2, EG_EW_2]
│   │   │       route_TL2: [510_NS_1, EG_WE_2, 510_SN_2, EG_EW_1]
│   │   │       route_TL3: [MT_NS_2, VV_WE_1, MT_SN_1, VV_EW_2]
│   │   │       route_TL4: [510_NS_2, VV_WE_2, 510_SN_1, VV_EW_1]
│   │   │   │
│   │   │   └── Waiting zones (Pedestres - Crossings + Walking Areas)
│   │   │   │
│   │   │   └── Funções de criação:
│   │   │       create_intersections()    → Dict{1,2,3,4: Intersection}
│   │   │       create_routes()           → Dict{1,2,3,4: route}
│   │   │       create_waiting_zones()    → Dict{1,2,3,4: zones}
│   │   │       create_tl_names()         → Dict{1,2,3,4: "J1","J2","J3","J4"}
│   │   │       create_incoming_routes()  → Estradas por célula
│   │   │       create_110_132_routes()   → Classificação por comprimento
│   │   │       create_map_environment()  → Mapa de índices agente→cruzamento
│   │   │
│   │   ├── generator.py                  [GERADOR DE TRÁFEGO DE VEÍCULOS]
│   │   │   └── TrafficGenerator class
│   │   │   └── Parâmetros: max_steps, n_cars_generated, scenario
│   │   │   └── Método: generate()        Cria rutas aleatórias para veículos
│   │   │
│   │   └── ped_generator.py              [GERADOR DE TRÁFEGO DE PEDESTRES]
│   │       └── PedestrianGenerator class
│   │       └── Parâmetros: max_steps, n_peds_generated
│   │       └── Método: generate()        Cria rotas para pedestres
│   │
│   ├── 📂 algorithms/                    [ALGORITMOS ESPECIALIZADOS]
│   │   └── sapa.py                       [SAPA - ADAPTIVE PHASE ADJUSTMENT]
│   │       └── sapa_module class
│   │       └── Parâmetros: dur_base=8, priority_ns=0.20, priority_ew=0.20
│   │       └── Método: sapa_block(idx, routes, map_env, action)
│   │           Função: Calcula duração dinâmica da fase verde
│   │           Entrada: índice do agente, rotas, mapa env, ação
│   │           Saída: duração em segundos adaptado ao tráfego
│   │
│   └── 📂 utils/                        [UTILITÁRIOS E VISUALIZAÇÃO]
│       ├── utils.py                      [Funções Auxiliares]
│       │   └── import_train_configuration()
│       │   └── import_test_configuration()
│       │   └── set_sumo()                Config do SUMO (GUI, config, max_steps)
│       │   └── set_train_path()          Cria pastas de output treino
│       │   └── set_test_path()           Cria pastas de output teste
│       │
│       └── visualization.py              [PLOTS E MÉTRICAS]
│           └── Visualization class
│           └── Método: save_data_and_plot()
│           └── Gera: PNG + TXT para cada métrica
│
├── 📂 config/                            [FICHEIROS DE CONFIGURAÇÃO]
│   ├── training_settings.ini             [Parâmetros de TREINO]
│   │   Seções:
│   │   - [model]        num_layers, width_layers, batch_size, learning_rate
│   │   - [memory]       memory_size_max, memory_size_min
│   │   - [simulation]   max_steps, green_duration, yellow_duration
│   │   - [training]     total_episodes, gamma (discount factor)
│   │   - [traffic]      n_cars_generated, n_peds_generated, scenario
│   │   - [paths]        models_path_name, sumocfg_file_name
│   │
│   └── testing_settings.ini              [Parâmetros de TESTE]
│       Seções:
│       - [simulation]   max_steps, green_duration, yellow_duration
│       - [model]        model_to_test (ex: "model_1")
│       - [network]      network (SUMO/REAL/BASELINE/FIXED)
│       - [paths]        models_path_name
│
├── 📂 models/                            [MODELOS TREINADOS E RESULTADOS]
│   │
│   ├── model_1/                          [MODELO 1 - VERSÃO BASELINE]
│   │   ├── Trained_Cell_1.h5             [Rede neural para J1+J3]
│   │   ├── Trained_Cell_2.h5             [Rede neural para J2+J4]
│   │   ├── MSE Loss Cell 1.txt           [Histórico de loss treino]
│   │   ├── MSE Loss Cell 2.txt
│   │   ├── Reward_C1.txt, Reward_C2.txt
│   │   ├── Reward_C3.txt, Reward_C4.txt
│   │   ├── training_settings.ini         [Config usada no treino]
│   │   │
│   │   ├── test_5000/                    [TESTE COM 5000 STEPS]
│   │   │   ├── Queue_1.txt, Queue_2.txt, Queue_3.txt, Queue_4.txt
│   │   │   ├── Average Phase Time in C1.txt ... C4.txt
│   │   │   ├── Average Waiting Time in C1.txt ... C4.txt
│   │   │   ├── Average Vehicle Speed C1.txt ... C4.txt
│   │   │   ├── Pedestrian Halting C1.txt ... C4.txt
│   │   │   ├── Agent Actions C1.txt ... C4.txt
│   │   │   ├── Lane Volume.txt
│   │   │   └── testing_settings.ini
│   │   │
│   │   ├── test_10000/                   [TESTE COM 10000 STEPS]
│   │   │   └── [Idem structure acima]
│   │   │
│   │   └── test_10003/                   [TESTE COM 10003 STEPS]
│   │       └── [Idem structure acima]
│   │
│   ├── model_2/                          [MODELO 2]
│   │   └── [Estrutura idêntica]
│   │
│   ├── model_3/                          [MODELO 3]
│   │   └── [Estrutura idêntica]
│   │
│   ├── model_4/                          [MODELO 4]
│   │   └── [Estrutura idêntica]
│   │
│   ├── model_5/                          [MODELO 5 - VERSÃO MAIS RECENTE]
│   │   ├── Trained_Cell_1.h5
│   │   ├── Trained_Cell_2.h5
│   │   ├── test_5000/, test_10000/, test_10003/
│   │   └── [Estrutura completa]
│   │
│   └── real_env/                         [MODO REAL (SEM IA) - BASELINE]
│       ├── test_5000/
│       ├── test_10000/
│       └── test_10003/
│
├── 📂 analysis/                          [SCRIPTS DE ANÁLISE PÓS-SIMULAÇÃO]
│   ├── data_processing.py                [Pré-processamento de dados]
│   ├── graphics_comparation.py           [Comparação visual entre modelos]
│   ├── phases_analasys.py                [Análise de fases]
│   └── analysis/
│       └── comparacao_graficos/          [Output: gráficos comparativos]
│
└── 📂 sumo/                              [CONFIGURAÇÃO DE SIMULAÇÃO SUMO]
    ├── sumo_config.sumocfg               [Arquivo principal de config]
    ├── osm.net.xml                       [Network - mapa das ruas]
    ├── episode_routes.rou.xml            [Rotas dos veículos]
    ├── pedestrian_routes.rou.xml         [Rotas dos pedestres]
    └── TL_combination.add.xml            [Configuração dos semáforos]
```

---

## 🧠 DETALHES TÉCNICOS DO SISTEMA

### 1️⃣ DDQN (Deep Double Q-Network)

**Conceito Base:**
- Agentes aprendem a controlar semáforos por **Reinforcement Learning**
- Utiliza **duas redes neurais**:
  - **Main Network**: Usada para gerar ações
  - **Target Network**: Usada para calcular Q-values alvo (mais estável)

**Parâmetros da Rede:**
```python
Input:  172 dimensões
  ├─ 164: Estado base (distribuição de veículos em células)
  ├─  2: Action encoding (one-hot dos 8 actions)
  └─  6: Lane occupancy (ocupação das 4 edges de entrada)

Hidden Layers: Configurável (default: 3-5 layers)
  └─ Width: 256-512 neurons (configurável)

Output: 8 ações (acciones de duração de fases)
  ├─ Action 0-7: Diferentes durações de verde NS/EW

Activation: ReLU (hidden), Linear (output)
Loss: Huber Loss
Optimizer: Adam (learning_rate = 0.001 default)
```

**Algoritmo DDQN em Pseudocódigo:**
```
Para cada step da simulação:
  1. Observar estado S
  2. Com probabilidade epsilon: ação aleatória
     Senão: ação = argmax(Main_Network.predict(S))
  3. Executar ação no SUMO
  4. Observar recompensa R e novo estado S'
  5. Armazenar (S, ação, R, S', done) em Memory
  6. Se Memory.size >= batch_size:
      Amostrar batch de experiências
      Q_targets = R + gamma * max(Target_Network(S'))
      Q_predictions = Main_Network(S)
      Loss = Huber(Q_targets, Q_predictions)
      Atualizar Main_Network com SGD
  7. A cada N steps: Main_Network → Target_Network (copy weights)
```

### 2️⃣ ESTADO (Observation Space)

**Dimensão Total: 172**

```
┌─────────────────────────────────────────────────────┐
│ DISTRIBUIÇÃO DE VEÍCULOS (164 dims)                │
│ ─────────────────────────────────────────────────── │
│ Para cada cruzamento (J1-J4):                       │
│  └─ 4 direções (N, O, S, E)                        │
│  └─ 10 células de distância (thresholds)           │
│  └─ Total: 4 * 10 * 4 = 160 dims                   │
│     (+ 4 dims adicionais de ajuste)                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ CODIFICAÇÃO DE AÇÃO (2 dims)                        │
│ ─────────────────────────────────────────────────── │
│ One-hot encoding de 8 ações possíveis              │
│ [0,0,0,0,0,0,0,0] ... [1,0,0,0,0,0,0,0]           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ OCUPAÇÃO DE FAIXAS (6 dims)                         │
│ ─────────────────────────────────────────────────── │
│ Ocupação das 4 edges de entrada (0-1 normalizadas)│
│ [occ_edge1, occ_edge2, occ_edge3, occ_edge4, 0, 0]│
└─────────────────────────────────────────────────────┘

TOTAL: 164 + 2 + 6 = 172 dimensões
```

**Método `get_state()` em `intersection.py`:**
```python
def get_state(self, idx, wz, routes, lanes_200_400, action):
    # 1. Inicializar array de 164 dims com zeros
    # 2. Para cada carro em cada edge de entrada:
    #    - Determinar posição relativa ao cruzamento
    #    - Mapear para célula de distância (0-9)
    #    - Incrementar state[lane_group * 10 + cell]
    #    - Adicionar velocidade normalizada
    # 3. Incorporar estado de pedestres
    # 4. Codificar ação em one-hot
    # 5. Adicionar ocupação de lanes
    # 6. Retornar array 172-dim
```

### 3️⃣ AÇÕES (Action Space)

**Dimensão: 8 ações**

```
Ação 0: PHASE_NS_GREEN   (NS = Norte-Sul, verde vertical)
Ação 1: PHASE_NS_YELLOW  (amarelo NS)
Ação 2: PHASE_NS_RED     (vermelho completo após NS)
Ação 3: PHASE_EW_GREEN   (EW = Este-Oeste, verde horizontal)
Ação 4: PHASE_EW_YELLOW  (amarelo EW)
Ação 5: PHASE_EW_RED     (vermelho completo após EW)
Ação 6: Ação reservada
Ação 7: Ação reservada
```

**Duração:**
- Verde: `green_duration` (default: 10 segundos) - **ADAPTÁVEL via SAPA**
- Amarelo: `yellow_duration` (default: 4 segundos) - **FIXO**

### 4️⃣ RECOMPENSA (Reward Function)

```python
# Em training_simulation.py
reward = -total_wait_time_vehicles - k * total_wait_time_pedestrians

# Negative reward baseado em tempos de espera
# k = weight factor para pedestres (default: 1.0 ou 0.5)

# Agentes tentam MINIMIZAR tempos de espera
# → Maior fluxo = menor tempo de espera = maior recompensa
```

### 5️⃣ SAPA (Smart Adaptive Phase Adjustment)

**Objetivo:** Ajustar dinamicamente a duração da fase verde baseado no tráfego atual

```python
sapa_block(idx, routes, map_env, action):
    """
    Entrada:
      - idx: índice do agente (1-4)
      - routes: rotas/edges de cada cruzamento
      - map_env: mapa de índices agente→cruzamento
      - action: ação escolhida (0-7)
    
    Processo:
      1. Extrair route para o cruzamento atual
      2. Contar carros esperando nos edges NS (Norte-Sul)
      3. Contar carros esperando nos edges EW (Este-Oeste)
      4. Se action = NS_GREEN:
         duration = base_duration * (1 + priority * queue_ns / max_queue)
      5. Se action = EW_GREEN:
         duration = base_duration * (1 + priority * queue_ew / max_queue)
    
    Saída: duração em segundos (adaptada ao tráfego)
    
    Resultado: Fases congestionadas recebem mais tempo verde
    """
```

---

## 🔄 FLUXO DE EXECUÇÃO

### TREINO (`training_main.py`)

```
1. INICIALIZAÇÃO
   ├─ Load configuração (training_settings.ini)
   ├─ Setup SUMO (GUI mode ou headless)
   ├─ Criar 2 modelos DDQN (Cell_1 para J1+J3, Cell_2 para J2+J4)
   ├─ Criar 2 buffers de memória (Memory_1, Memory_2)
   ├─ Inicializar geradores de tráfego (veículos + pedestres)
   └─ Criar 4 agentes Intersection

2. PARA CADA EPISÓDIO (1 a total_episodes):
   
   a) WARM-UP (3 episódios iniciais com ε=1.0)
      ├─ Exploração pura (ações aleatórias)
      └─ Preencher Experience Replay com experiências iniciais
   
   b) TREINO PRINCIPAL (com ε decrescente)
      ├─ LOOP SIMULAÇÃO (step=0 a max_steps):
      │  ├─ Gerar novos veículos/pedestres conforme scenario
      │  │
      │  ├─ PARA CADA CRUZAMENTO (J1-J4):
      │  │  ├─ Observar estado S (172-dim)
      │  │  ├─ Agente decide ação:
      │  │  │   Com prob ε: ação aleatória
      │  │  │   Senão: ação = argmax(DDQN(S))
      │  │  ├─ Executar ação no SUMO (set_green/yellow/red phase)
      │  │  ├─ Duração verde via SAPA (adaptativa)
      │  │  └─ Armazenar (S, ação, state_intermediate) para pós-processamento
      │  │
      │  ├─ Simular 1 step no SUMO (1 segundo de tráfego)
      │  │
      │  ├─ COLETAR RECOMPENSA:
      │  │  ├─ Tempo de espera total de veículos (por cruzamento)
      │  │  ├─ Tempo de espera de pedestres (por cruzamento)
      │  │  ├─ Calcular reward = -(wait_veh + k*wait_ped)
      │  │  └─ Negativa = incentiva minimização
      │  │
      │  ├─ PARA CADA CRUZAMENTO (J1-J4):
      │  │  ├─ Observar novo estado S'
      │  │  ├─ Determinar done = (step == max_steps)
      │  │  ├─ Armazenar experience (S, ação, reward, S', done) em Memory
      │  │  │   └─ Memory_1 para J1,J3; Memory_2 para J2,J4
      │  │  │
      │  │  └─ TREINAR SE MEMORY.SIZE >= BATCH_SIZE:
      │  │     ├─ Amostrar batch de n experiências aleatórias
      │  │     ├─ Calcular Q-targets:
      │  │     │   Q_target = r + γ * max(Target_Network(S')) se not done
      │  │     │   Q_target = r                              se done
      │  │     ├─ Calcular Q-predictions:
      │  │     │   Q_pred = Main_Network(S)
      │  │     ├─ Calcular loss = Huber(Q_target, Q_pred)
      │  │     └─ Backprop e atualizar Main_Network pesos
      │  │
      │  └─ A cada N_COPY_WEIGHTS steps:
      │     └─ Copy Main_Network → Target_Network (estabilidade)
      │
      ├─ FIM LOOP SIMULAÇÃO
      │
      ├─ ESTATÍSTICAS DO EPISÓDIO:
      │  ├─ Recompensa total por cruzamento
      │  ├─ Tempo médio de espera por cruzamento
      │  ├─ Loss médio da rede
      │  └─ Print à consola
      │
      ├─ DECAY EPSILON:
      │  └─ ε = ε * epsilon_decay (default: 0.995)
      │
      └─ A cada N episódios:
         └─ Save modelo (Trained_Cell_1.h5, Trained_Cell_2.h5)

3. FIM TREINO
   ├─ Save modelos finais
   ├─ Save histórico de losses (MSE Loss Cell 1.txt, etc)
   ├─ Save histórico de recompensas (Reward_C1.txt, etc)
   └─ Print tempo total de execução
```

### TESTE (`testing_main.py`)

```
1. INICIALIZAÇÃO
   ├─ Load configuração (testing_settings.ini)
   ├─ Determinar modo: 'SUMO' (com modelos) vs 'REAL'/'BASELINE'/'FIXED' (sem IA)
   ├─ Se SUMO: Load modelos treinados (Trained_Cell_1.h5, Trained_Cell_2.h5)
   ├─ Setup SUMO
   ├─ Inicializar geradores de tráfego
   └─ Criar 4 agentes Intersection + estruturas de armazenamento de métricas

2. EXECUTAR SIMULAÇÃO (1 episódio com seed fixa para reprodutibilidade)
   ├─ LOOP SIMULAÇÃO (step=0 a max_steps):
   │  ├─ Gerar tráfego com seed (reprodutível)
   │  │
   │  ├─ PARA CADA CRUZAMENTO:
   │  │  ├─ Observar estado S
   │  │  ├─ Se modo SUMO: ação = argmax(DDQN(S)) [SEM exploração, ε=0]
   │  │  │   Senão: ação = fase fixa pré-definida
   │  │  ├─ Executar ação com duração (SAPA se SUMO, fixa se REAL)
   │  │  └─ Armazenar métrica de ação escolhida
   │  │
   │  ├─ Simular 1 step em SUMO
   │  │
   │  └─ COLETAR MÉTRICAS (para análise posterior):
   │     ├─ Queue length (comprimento de fila por cruzamento)
   │     ├─ Average waiting time (tempo médio espera por cruzamento)
   │     ├─ Average vehicle speed na zona verde
   │     ├─ Pedestrian halting count (pedestres parados)
   │     ├─ Phase duration (duração de cada fase ativada)
   │     ├─ Lane volume (volume de tráfego por avenida)
   │     └─ Agent actions log (ações escolhidas por agente)
   │
   └─ FIM LOOP

3. SALVAR RESULTADOS
   ├─ Para cada métrica:
   │  ├─ Exportar para TXT
   │  ├─ Gerar gráfico PNG (matplotlib)
   │  └─ Salvar em test_X/ folder (X = episode_seed)
   │
   └─ Salvar testing_settings.ini para rastreabilidade
```

---

## 📊 MÉTRICAS COLETADAS E ARMAZENADAS

### Durante TREINO

| Métrica | Descrição | Armazenado em |
|---------|-----------|---------------|
| **Reward per Intersection** | Recompensa total por cruzamento por episódio | `Reward_C1.txt` ... `Reward_C4.txt` |
| **Training Loss** | Loss da rede DDQN por episódio | `MSE Loss Cell 1.txt`, `MSE Loss Cell 2.txt` |
| **Cumulative Wait** | Tempo total espera acumulado | Internamente (intersections) |
| **Epsilon Decay** | Evolução da taxa exploração | Implícito no treino |

### Durante TESTE

| Métrica | Descrição | Ficheiro Output |
|---------|-----------|-----------------|
| **Queue Length** | Comprimento fila de veículos (por time step) | `Queue_1.txt` ... `Queue_4.txt` |
| **Average Phase Time** | Duração média da fase verde | `Average Phase Time in C1.txt` ... |
| **Average Waiting Time** | Tempo médio espera de veículos | `Average Waiting Time in C1.txt` ... |
| **Average Vehicle Speed** | Velocidade média em zona verde | `Average Vehicle Speed C1.txt` ... |
| **Pedestrian Halting** | Número pedestres parados em cada time step | `Pedestrian Halting C1.txt` ... |
| **Agent Actions Log** | Ações escolhidas por agente por time step | `Agent Actions C1.txt` ... |
| **Lane Volume** | Volume total de tráfego por avenida | `Lane Volume.txt` |

### Análise Comparativa (Scripts em `analysis/`)

- **Comparação entre modelos** (model_1 vs model_5, etc)
- **Baseline vs REAL mode** (modelos IA vs controladores fixos)
- **Análise de fases** (duração e efetividade)
- **Gráficos comparativos** (salvos em `analysis/comparacao_graficos/`)

---

## ⚙️ PARÂMETROS CONFIGURÁVEIS

### `config/training_settings.ini`

```ini
[model]
num_layers = 3                    # Número de hidden layers na DDQN
width_layers = 256                # Neurons por hidden layer
batch_size = 32                   # Tamanho do mini-batch
learning_rate = 0.001             # Taxa aprendizagem Adam

[memory]
memory_size_max = 100000          # Máximo de experiências em replay buffer
memory_size_min = 600             # Mínimo antes de começar treino

[simulation]
max_steps = 5400                  # Passos por episódio (90 minutos simulados)
green_duration = 10               # Duração verde (segundos) - BASE
yellow_duration = 4               # Duração amarelo (segundos) - FIXO

[training]
total_episodes = 100              # Número episódios treino
gamma = 0.75                      # Discount factor (0.75 = curto prazo)
epsilon_decay = 0.995             # Decay por episódio (1.0 - 0.995 = 0.005)

[traffic]
n_cars_generated = 1000           # Carros por episódio
n_peds_generated = 100            # Pedestres por episódio
scenario = "random"               # Tipo geração tráfego

[gui]
gui = False                       # Ativar GUI SUMO (lento!)

[paths]
models_path_name = "models"       # Pasta output modelos
sumocfg_file_name = "sumo/sumo_config.sumocfg"
```

### `config/testing_settings.ini`

```ini
[simulation]
max_steps = 10000                 # Passos teste
green_duration = 10
yellow_duration = 4

[model]
model_to_test = "model_5"         # Qual modelo carregar
num_states = 172
num_actions = 8

[network]
network = "SUMO"                  # SUMO (IA), REAL (fixo), BASELINE, FIXED

[paths]
models_path_name = "models"
episode_seed = 10000              # Seed para reprodutibilidade
```

---

## 🔧 INSTALAÇÃO E EXECUÇÃO

### Requisitos

```
Python 3.8+
TensorFlow 2.10+
SUMO 1.14+ (instalado e acessível via `sumo` ou `sumo.exe`)
```

### Setup

```bash
# 1. Clone/copie o projeto
cd Projeto

# 2. Instale dependências
pip install -r requirements.txt

# 3. Verifique SUMO
sumo --version  # Deve mostrar versão

# 4. Teste treino (1 episódio rápido para debug)
python training_main.py --config config/training_settings.ini

# 5. Teste teste
python testing_main.py --config config/testing_settings.ini
```

---

## 📈 ESTRUTURA DE DADOS INTERNAS

### Objeto `Intersection`

```python
class Intersection:
    # Identificação
    self.id = 1, 2, 3 ou 4        # J1, J2, J3, J4
    
    # Configuração
    self.green_duration = 10       # Segundos
    self.yellow_duration = 4       # Segundos
    self.num_states = 172          # Dimensão estado
    
    # Estado Treino
    self.reward_episode = []       # Lista de recompensas
    self.cumulative_wait = []      # Tempos espera acumulados
    self.sum_neg_reward = 0        # Soma rewards negativos
    self.wait_veh = 0              # Wait time veículos atual
    self.wait_ped = 0              # Wait time pedestres atual
    self.old_state = None          # Estado anterior
    self.old_action = -1           # Ação anterior
    
    # Estado Teste
    self.queue_length = []         # Fila ao longo tempo
    self.phase_activated = []      # Fases ativadas
    self.awt_greenArea = []        # Avg wait na zona verde
    self.pedestrians_halting = []  # Pedestres parados
    self.phase_duration = [0]*8    # Duração acumulada por fase
    self.n_times_active = [0]*8    # Contagem vezes por fase
```

### Experience Replay Buffer

```python
Memory._samples = [
    (state, action, reward, next_state, done),  # Sample 1
    (state, action, reward, next_state, done),  # Sample 2
    ...
    (state, action, reward, next_state, done),  # Sample N
]
# Max tamanho: memory_size_max (default 100k)
# Min para treinar: memory_size_min (default 600)
```

---

## 🎓 ALGORITMO DE RL - RESUMO TEÓRICO

**DDQN = Deep Double Q-Network**

```
Standard Q-Learning:
  Q(s,a) = Q(s,a) + α[r + γ*max_a' Q(s',a') - Q(s,a)]

Deep Q-Network (DQN):
  Q(s,a) = NN_main(s) → value para cada ação
  Target = r + γ*max_a' NN_target(s')

Double DQN (DDQN) - MAIS ESTÁVEL:
  best_action = argmax_a' NN_main(s')      # Seleciona com main
  Target = r + γ*NN_target(s', best_action)  # Avalia com target
  
Benefício: Reduz overestimation de Q-values
```

**Experience Replay:**
- Armazena (s,a,r,s',done) tuplas
- Amostra aleatórias em mini-batches → quebra correlação
- Melhora estabilidade e sample efficiency

**Epsilon-Greedy Exploration:**
```
ação = { aleatória           com probabilidade ε
       { argmax(NN(s))       com probabilidade 1-ε

ε decai ao longo do treino → Mais exploitation, menos exploração
```

---

## 🐛 POSSÍVEIS EXTENSÕES E MELHORIAS

1. **Comunicação Inter-Agente**: Adicionar troca de informações entre J1-J4
2. **Curb Management**: Gestão de estacionamento em curb
3. **Detecção de Incidentes**: Acidentes, ruas bloqueadas
4. **Modelo Multi-Task**: Um modelo único para todas as interseções
5. **Algoritmos Avançados**: PPO, A3C, MADDPG para coordenação
6. **Mobile Agent Swarms**: Múltiplas células urbanas
7. **Real-World Deployment**: Integração com sistemas reais de tráfego
8. **Transfer Learning**: Treino em um cenário, teste noutro

---

## 📝 FICHEIROS CHAVE COMENTADOS

### `intersection.py` - Núcleo da Lógica de Estado/Ação

**Responsabilidades:**
1. Calcular estado observável de um cruzamento (172-dim vector)
2. Aplicar ações (mudar fase de semáforo)
3. Colectar recompensas (tempos de espera)
4. Rastrear métricas (queue, speed, pedestrians)

**Métodos Críticos:**
- `get_state()`: Extrai feature vector 172-dim do SUMO
- `choose_phase()`: Decide verde vs amarelo
- `set_green_phase()` / `set_yellow_phase()`: Aplica ação em SUMO
- `pedestrians_state()`: Incorpora pedestres no estado
- `lane_occupancy()`: Adiciona ocupação de faixas
- `action_encode()`: Codifica ação em one-hot

### `model.py` - Rede Neural DDQN

**Classes:**
- `TrainModel`: 2 redes (main + target) para treino
- `TestModel`: 1 rede carregada para inferência

**Métodos:**
- `_build_model()`: Construir rede fully-connected
- `predict_one()`: Predição single state
- `predict_batch()` / `predict_batch_target()`: Batch predictions
- `train_batch()`: Atualizar pesos com experience batch
- `copy_weights()`: Main → Target (DDQN stability)
- `save_model()` / `load_model()`: Persistência

### `training_simulation.py` - Loop de Treino

**Responsabilidades:**
1. Inicializar SUMO com tráfego
2. Para cada step: observar → decidir → executar → treinar
3. Gerir epsilon-decay
4. Salvar modelos periodicamente

**Método `run(episode, epsilon, warm_up)`:**
- Executa 1 episódio completo (5400 steps)
- Retorna tempo simulação e tempo treino

### `testing_simulation.py` - Loop de Teste

**Responsabilidades:**
1. Executar modelo treinado (ou baseline)
2. Colectar métricas detalhadas
3. Salvar resultados para análise

**Modos:**
- `network = "SUMO"`: Usa modelos treinados
- `network = "REAL"`: Controlador fixo (baseline)
- `network = "BASELINE"`: Controlo estático
- `network = "FIXED"`: Controlo pre-definido

### `intersection_manager.py` - Orquestração

**Funções de Inicialização:**
- `create_intersections()`: Instancia 4 Intersection objects
- `create_routes()`: Define edges por cruzamento
- `create_waiting_zones()`: Zonas pedestres
- `create_tl_names()`: Mapeamento indices↔nomes SUMO
- `create_map_environment_()`: Mapa agente→cruzamento

---

## 🔗 FLUXO DE DADOS VISUALMENTE

```
SUMO (Simulation)
    ↓ (TraCI API)
    ↓
Intersection.get_state()  ← Extrai 172-dim feature vector
    ↓
DDQN Model.predict()      ← Prediz Q-values para 8 ações
    ↓
Argmax (sem exploração)   ← Escolhe ação com maior Q-value
    ↓
Intersection.choose_phase() ← Aplica ação (verde/amarelo/vermelho)
    ↓
SAPA.sapa_block()         ← Calcula duração adaptativa
    ↓
SUMO.trafficlight.setPhase() ← Atualiza semáforo em simulação
    ↓ (1 segundo passa)
    ↓
Colecta Rewards (wait times)
    ↓
Experience Replay Buffer   ← Armazena (S,A,R,S',done)
    ↓
DDQN Model.train_batch()  ← Treina rede com experiências
    ↓ (a cada N steps)
    ↓
Copy Weights              ← Main → Target (estabilidade)
    ↓
Loop volta ao início ↻
```

---

## 📚 RESUMO ARQUIVOS CORE

| Ficheiro | Linhas | Função |
|----------|--------|--------|
| `src/agents/intersection.py` | ~200 | Lógica de estado/ação/reward por cruzamento |
| `src/agents/model.py` | ~80 | Rede neural DDQN (main + target) |
| `src/agents/memory.py` | ~30 | Buffer experience replay |
| `src/simulation/training_simulation.py` | ~300 | Loop treino principal |
| `src/simulation/testing_simulation.py` | ~400 | Loop teste + coleta métricas |
| `src/simulation/intersection_manager.py` | ~100 | Inicialização de cruzamentos |
| `src/algorithms/sapa.py` | ~80 | Ajuste adaptativo duração fases |
| `src/utils/utils.py` | ~100 | Config + setup SUMO |
| `src/utils/visualization.py` | ~50 | Plots e export métricas |

---

## 🎯 COMO USAR ESTE DOCUMENTO

**Para Compreender o Projeto:**
1. Comece por "Resumo Executivo" e "Objetivos"
2. Estude "Arquitetura Geral"
3. Explore "Estrutura de Pastas"
4. Leia "DDQN (Deep Double Q-Network)"

**Para Treinar:**
1. Edite `config/training_settings.ini`
2. Execute: `python training_main.py`
3. Monitor loss em `models/model_X/MSE Loss Cell*.txt`

**Para Testar:**
1. Edite `config/testing_settings.ini`
2. Especifique `model_to_test = "model_X"`
3. Execute: `python testing_main.py`
4. Analise resultados em `models/model_X/test_X/`

**Para Entender Fluxo de Dados:**
1. Veja "Fluxo de Execução"
2. Trace através de "Fluxo de Dados Visualmente"
3. Estude métodos em "Ficheiros Chave Comentados"

---

## 📞 CONTACTOS E SUPORTE

**Documentação SUMO:** https://sumo.dlr.de/docs/
**TraCI Python API:** https://sumo.dlr.de/docs/TraCI/

**Bibliotecas Principais:**
- TensorFlow/Keras: https://www.tensorflow.org/
- NumPy: https://numpy.org/
- Matplotlib: https://matplotlib.org/

---

**Documento Gerado:** 1 de Maio de 2026
**Versão:** 1.0 MEGA COMPLETO
**Status:** Pronto para Produção e Análise
