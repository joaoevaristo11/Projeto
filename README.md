# 🚦 Sistema Multi-Agente de Controlo de Tráfego com DDQN

> Um sistema inteligente de gestão de tráfego urbano utilizando Deep Double Q-Learning (DDQN) para controlar 9 interseções de forma coordenada e adaptativa.

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Configuração](#configuração)
- [Detalhes Técnicos](#detalhes-técnicos)

---

## 🎯 Sobre o Projeto

Este projeto implementa um **sistema multi-agente de controlo de tráfego** baseado em **aprendizagem por reforço profundo**. Através do algoritmo **DDQN (Deep Double Q-Network)**, o sistema aprende a controlar semáforos em 9 interseções de forma inteligente, minimizando tempos de espera de veículos e pedestres.

### Características Principais

- ✅ **9 Agentes Inteligentes** controlando interseções independentes
- ✅ **Aprendizagem por Reforço** com redes neuronais profundas (TensorFlow/Keras)
- ✅ **Simulação Realista** usando SUMO (Simulation of Urban MObility)
- ✅ **Gestão de Tráfego Misto** (veículos + pedestres)
- ✅ **Adaptação Dinâmica** com módulo SAPA para ajuste de fases
- ✅ **Análise Completa** com métricas e visualizações

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    SUMO (Simulador)                     │
│              (Ambiente de Tráfego Urbano)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Módulo de Simulação (TraCI)                │
│        (Comunicação Python ↔ SUMO em tempo real)        │
└──────┬──────────────────────────────────────────┬───────┘
       │                                          │
       ▼                                          ▼
┌───────────────┐                        ┌───────────────┐
│  Célula 1     │                        │  Célula 2     │
│  (5 Agentes)  │                        │  (4 Agentes)  │
│               │                        │               │
│  ┌─────────┐  │                        │  ┌─────────┐  │
│  │ Agent 0 │  │                        │  │ Agent 5 │  │
│  │ Agent 1 │  │                        │  │ Agent 6 │  │
│  │ Agent 2 │  │                        │  │ Agent 7 │  │
│  │ Agent 3 │  │                        │  │ Agent 8 │  │
│  │ Agent 4 │  │                        │             │  │
│  └─────────┘  │                        │  └─────────┘  │
│       │       │                        │       │       │
│       ▼       │                        │       ▼       │
│  DDQN Model 1 │                        │  DDQN Model 2 │
│  (TensorFlow) │                        │  (TensorFlow) │
└───────────────┘                        └───────────────┘
```

### Componentes Principais

1. **SUMO**: Simulador de tráfego que gera cenários realistas
2. **Agentes DDQN**: Tomam decisões sobre fases dos semáforos
3. **Experience Replay**: Memória para treino eficiente
4. **SAPA**: Módulo de ajuste adaptativo de duração de fases
5. **Visualização**: Gera gráficos e métricas de desempenho

---

## 📁 Estrutura do Projeto

```
Multi-Agent-DDQN-Traffic-Control-System/
│
├── 📂 src/                          # Código-fonte principal
│   ├── 📂 agents/                   # Agentes de RL
│   │   ├── model.py                 # Rede neural DDQN (TensorFlow)
│   │   ├── memory.py                # Experience Replay Buffer
│   │   └── intersection.py          # Classe Intersection (estado/ações)
│   │
│   ├── 📂 simulation/               # Lógica de simulação SUMO
│   │   ├── training_simulation.py  # Loop de treino
│   │   ├── testing_simulation.py   # Loop de teste
│   │   ├── generator.py             # Geração de tráfego de veículos
│   │   ├── ped_generator.py         # Geração de tráfego de pedestres
│   │   └── intersection_manager.py  # Gestão das 9 interseções
│   │
│   ├── 📂 algorithms/               # Algoritmos especializados
│   │   └── sapa.py                  # SAPA (ajuste adaptativo de fases)
│   │
│   └── 📂 utils/                    # Utilitários
│       ├── utils.py                 # Funções auxiliares (config, SUMO)
│       └── visualization.py         # Geração de gráficos
│
├── 📂 sumo/                         # Ficheiros do simulador SUMO
│   ├── network.net.xml              # Rede de tráfego (1 interseção)
│   ├── network_5_intersections.net.xml  # Rede com 9 interseções
│   ├── sumo_config.sumocfg          # Configuração principal SUMO
│   ├── TL_combination.add.xml       # Definição de fases dos semáforos
│   ├── episode_routes.rou.xml       # Rotas de veículos (gerado)
│   └── pedestrian_routes.rou.xml    # Rotas de pedestres (gerado)
│
├── 📂 config/                       # Ficheiros de configuração
│   ├── training_settings.ini        # Parâmetros de treino
│   └── testing_settings.ini         # Parâmetros de teste
│
├── 📂 analysis/                     # Scripts de análise pós-treino
│   ├── data_processing.py           # Processamento de resultados (Excel)
│   ├── graphics_comparation.py      # Comparação entre estratégias
│   └── phases_analasys.py           # Análise de distribuição de fases
│
├── 📂 models/                       # Modelos treinados (gerado)
│   └── model_X/                     # Cada treino cria uma nova pasta
│       ├── Trained_Cell_1.h5        # Modelo da Célula 1
│       ├── Trained_Cell_2.h5        # Modelo da Célula 2
│       └── test_XXXX/               # Resultados dos testes
│
├── training_main.py                 # 🚀 Script principal de TREINO
├── testing_main.py                  # 🧪 Script principal de TESTE
├── requirements.txt                 # Dependências Python
└── README.md                        # Este ficheiro
```

---

## 🔍 Descrição Detalhada dos Ficheiros

### 📂 `src/agents/` - Agentes de Aprendizagem

#### **`model.py`**
Define as redes neuronais DDQN usando TensorFlow/Keras.

- **`TrainModel`**: Rede para treino
  - Arquitetura: Input → Dense(ReLU) → ... → Dense(Linear) → Output
  - Otimizador: Adam
  - Loss: Huber Loss
  - Métodos: `predict_one()`, `train_batch()`, `copy_weights()`

- **`TestModel`**: Carrega modelos treinados para teste
  - Carrega ficheiros `.h5` salvos
  - Apenas inferência (sem treino)

#### **`memory.py`**
Implementa o **Experience Replay Buffer**.

- Armazena transições `(state, action, reward, next_state, done)`
- Amostragem aleatória para quebrar correlações temporais
- Tamanho configurável (min/max)

#### **`intersection.py`**
Classe que representa cada **interseção individual**.

- **Estado**: fila de espera, posições de veículos, pedestres
- **Ações**: 9 fases possíveis dos semáforos
- **Recompensa**: baseada em tempo de espera
- Gestão de fases (verde, amarelo, vermelho)

### 📂 `src/simulation/` - Simulação SUMO

#### **`training_simulation.py`**
Loop principal de treino com **ε-greedy exploration**.

- Executa episódios de treino
- Coleta experiências para o replay buffer
- Atualiza redes Q e Target Q periodicamente
- Salva métricas por episódio

#### **`testing_simulation.py`**
Loop de teste usando **política greedy pura** (sem exploração).

- Avalia modelos treinados
- Recolhe métricas detalhadas (filas, velocidades, tempos de espera)
- Gera relatórios de desempenho

#### **`generator.py`**
Gera tráfego de veículos com **distribuição Weibull**.

- 5 cenários pré-definidos (circular vs. radial)
- Rotas aleatórias entre interseções
- Ficheiro de saída: `episode_routes.rou.xml`

#### **`ped_generator.py`**
Gera tráfego de pedestres.

- Distribuição temporal aleatória
- Travessias em todas as interseções
- Ficheiro de saída: `pedestrian_routes.rou.xml`

#### **`intersection_manager.py`**
Gestão centralizada das 9 interseções.

- Mapeamento de IDs (J0-J8 → C0-C8)
- Definição de faixas de rodagem por interseção
- Zonas de espera de pedestres
- Coordenação entre células

### 📂 `src/algorithms/` - Algoritmos

#### **`sapa.py`**
**SAPA** (Self-Adaptive Phase Adjustment).

- Ajusta dinamicamente a duração de fases verdes
- Baseado em densidade de tráfego
- Prioriza rotas circulares vs. radiais conforme cenário
- Adapta-se à posição da interseção na rede

### 📂 `src/utils/` - Utilitários

#### **`utils.py`**
Funções auxiliares gerais.

- `import_train_configuration()`: lê `training_settings.ini`
- `import_test_configuration()`: lê `testing_settings.ini`
- `set_sumo()`: configura comando SUMO
- `set_train_path()`: cria pasta para modelo novo
- `set_test_path()`: prepara pasta para resultados de teste

#### **`visualization.py`**
Gera gráficos e salva dados.

- `save_data_and_plot()`: gráfico de linha + ficheiro `.txt`
- `save_data_and_barchart()`: gráfico de barras
- Usa Matplotlib com estilo profissional

### 📂 `sumo/` - Configuração SUMO

#### **`network.net.xml`** / **`network_5_intersections.net.xml`**
Ficheiros de rede de tráfego criados com NETEDIT.

- Define ruas, cruzamentos, faixas
- Topologia da cidade simulada

#### **`sumo_config.sumocfg`**
Configuração principal do SUMO.

- Aponta para ficheiros de rede e rotas
- Define tempo de simulação
- Parâmetros gerais

#### **`TL_combination.add.xml`**
Define as **8 fases** de cada semáforo.

- Fases NS (Norte-Sul), WE (Oeste-Este)
- Direções: frente, todas, esquerda
- Fases de pedestres

#### **`episode_routes.rou.xml`** *(gerado automaticamente)*
Rotas de veículos para o episódio atual.

#### **`pedestrian_routes.rou.xml`** *(gerado automaticamente)*
Rotas de pedestres para o episódio atual.

### 📂 `config/` - Configurações

#### **`training_settings.ini`**
Parâmetros de treino.

```ini
[simulation]
gui = False                 # Mostrar interface gráfica?
total_episodes = 200        # Número de episódios
max_steps = 3600           # Passos por episódio (1h simulada)
n_cars_generated = 2600    # Carros gerados
n_peds_generated = 1000    # Pedestres gerados
scenario = 5               # Cenário de tráfego (1-5)

[model]
num_layers = 2             # Camadas escondidas
width_layers = 256         # Neurónios por camada
batch_size = 128           # Tamanho do batch
learning_rate = 0.0001     # Taxa de aprendizagem
training_epochs = 50       # Épocas por treino

[memory]
memory_size_min = 600      # Mínimo para começar treino
memory_size_max = 100000   # Tamanho máximo do buffer

[agent]
num_states = 181           # Dimensão do estado
num_actions = 9            # Número de ações (fases)
gamma = 0.75               # Factor de desconto
```

#### **`testing_settings.ini`**
Parâmetros de teste + indica modelo a testar.

### 📂 `analysis/` - Análise de Resultados

#### **`data_processing.py`**
Processa resultados e gera ficheiros Excel com gráficos.

- Lê ficheiros `.txt` de métricas
- Cria workbook com múltiplas métricas
- Gera gráficos de linha automáticos

#### **`graphics_comparation.py`**
Compara diferentes estratégias/modelos.

- Sobreposição de resultados
- Análise estatística
- Exporta PDFs/PNGs

#### **`phases_analasys.py`**
Analisa distribuição de uso de fases.

- Percentagem de tempo em cada fase
- Gráficos de barras por agente
- Ficheiro Excel com resultados

### 🚀 Scripts Principais

#### **`training_main.py`**
**Ponto de entrada para TREINO**.

1. Carrega configurações
2. Inicializa 2 modelos DDQN (Célula 1 e 2)
3. Cria buffers de memória
4. Executa simulação de treino
5. Salva modelos treinados
6. Gera gráficos de aprendizagem

**Uso:**
```bash
python training_main.py
```

#### **`testing_main.py`**
**Ponto de entrada para TESTE**.

1. Carrega configurações de teste
2. Carrega modelos treinados
3. Executa simulação de teste
4. Recolhe métricas detalhadas
5. Gera relatório completo

**Uso:**
```bash
python testing_main.py
```

---

## 💻 Requisitos

### Software Necessário

| Requisito | Versão | Notas |
|-----------|--------|-------|
| **Python** | 3.11 ou 3.12 | ⚠️ Python 3.14 **não** é compatível com TensorFlow |
| **SUMO** | 1.12+ | Simulador de tráfego |
| **pip** | Mais recente | Gestor de pacotes Python |

### Bibliotecas Python

- **TensorFlow** ≥ 2.10.0 - Redes neuronais
- **NumPy** - Computação numérica
- **Pandas** - Processamento de dados
- **Matplotlib** - Visualizações
- **OpenPyXL** - Manipulação de Excel
- **TraCI/sumolib** - Interface com SUMO

---

## 🛠️ Instalação

### 1. Instalar Python 3.11

⚠️ **IMPORTANTE**: TensorFlow não funciona com Python 3.14!

**Download:** https://www.python.org/downloads/release/python-3119/

Durante a instalação, marca **"Add Python to PATH"**.

### 2. Instalar SUMO

**Download:** https://www.eclipse.org/sumo/

**Depois da instalação:**

1. Adiciona variável de ambiente `SUMO_HOME`:
   - Windows: Painel de Controlo → Sistema → Variáveis de Ambiente
   - Exemplo: `C:\Program Files (x86)\Eclipse\Sumo`

2. Verifica:
```cmd
echo %SUMO_HOME%
```

### 3. Clonar/Descarregar o Projeto

```bash
git clone <url-do-repositorio>
cd Multi-Agent-DDQN-Traffic-Control-System-main
```

### 4. Criar Ambiente Virtual

```cmd
# Criar venv com Python 3.11
py -3.11 -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Deves ver (venv) no terminal
```

### 5. Instalar Dependências

```cmd
# Atualizar pip
python -m pip install --upgrade pip

# Instalar bibliotecas
pip install -r requirements.txt
```

### 6. Verificar Instalação

```cmd
python -c "import tensorflow; import numpy; import traci; print('✅ Tudo OK!')"
```

---

## 🚀 Como Usar

### Treinar um Modelo Novo

1. **Edita configurações** (opcional):
   ```
   config/training_settings.ini
   ```

2. **Executa treino**:
   ```cmd
   python training_main.py
   ```

3. **Aguarda** (pode demorar horas/dias dependendo de `total_episodes`)

4. **Resultados** salvos em:
   ```
   models/model_X/
   ```

### Testar um Modelo Treinado

1. **Configura modelo a testar**:
   ```ini
   # config/testing_settings.ini
   [dir]
   model_to_test = 1  # Número do modelo
   ```

2. **Executa teste**:
   ```cmd
   python testing_main.py
   ```

3. **Resultados** em:
   ```
   models/model_X/test_YYYY/
   ```

### Ver Simulação com GUI

Para ver a simulação graficamente:

```ini
# Em training_settings.ini ou testing_settings.ini
[simulation]
gui = True  # Ativa interface SUMO
```

⚠️ **Nota**: GUI deixa treino/teste **muito mais lento**.

---

## ⚙️ Configuração

### Cenários de Tráfego

5 cenários pré-definidos (`scenario = 1-5` em `.ini`):

| Cenário | Tráfego Circular | Tráfego Radial | Descrição |
|---------|------------------|----------------|-----------|
| 1 | 50% | 50% | Balanceado |
| 2 | 65% | 75% | Alto (ambos) |
| 3 | 65% | 25% | Circular dominante |
| 4 | 25% | 75% | Radial dominante |
| 5 | 25% | 25% | Baixo (ambos) |

### Ajuste de Hiperparâmetros

**Para melhorar desempenho:**

```ini
[model]
num_layers = 3          # Mais camadas = mais capacidade
width_layers = 512      # Mais neurónios = mais expressividade
learning_rate = 0.0005  # Maior = aprende mais rápido (mas instável)

[agent]
gamma = 0.90            # Maior = planeia mais a longo prazo
```

**Para acelerar treino:**

```ini
[simulation]
total_episodes = 50     # Menos episódios
max_steps = 1800        # Episódios mais curtos

[model]
batch_size = 256        # Batches maiores (requer mais RAM)
```

---

## 📊 Detalhes Técnicos

### Algoritmo DDQN

**Deep Double Q-Network** é uma evolução do DQN que resolve o problema de sobreestimação de Q-values.

**Diferença-chave:**
- **DQN**: Usa mesma rede para selecionar e avaliar ação
- **DDQN**: Usa rede principal para selecionar, target network para avaliar

**Equação de Bellman:**
```
Q(s,a) ← Q(s,a) + α[r + γ·Q_target(s', argmax_a' Q_main(s',a')) - Q(s,a)]
```

### Estado do Agente

Cada interseção observa:

- **Densidade de veículos** por faixa (8 faixas)
- **Posições discretizadas** de veículos próximos
- **Fila de espera** de veículos
- **Pedestres em espera** (4 zonas)
- **Fase atual** do semáforo
- **Duração da fase** atual

**Total**: 181 valores numéricos

### Espaço de Ações

9 fases possíveis:

1. NS Frente/Direita
2. Norte Todas as direções
3. Sul Todas as direções
4. NS Esquerda
5. WE Frente/Direita
6. Oeste Todas as direções
7. Este Todas as direções
8. WE Esquerda
9. Pedestres (todas as direções)

### Função de Recompensa

```
reward = -(wait_time_vehicles + β·wait_time_pedestrians)
```

Penaliza tempo de espera acumulado. O objetivo é **maximizar** esta recompensa (minimizar esperas).

### Arquitetura da Rede

```
Input (181) 
    ↓
Dense(256, ReLU)
    ↓
Dense(256, ReLU)
    ↓
Dense(9, Linear)  ← Q-values para cada ação
```

---

## 📈 Métricas Avaliadas

Durante treino/teste, são recolhidas:

- **Reward** acumulado por episódio
- **Queue Length** (comprimento da fila)
- **Average Waiting Time** (tempo médio de espera)
- **Pedestrian Halting** (pedestres em espera)
- **Average Speed** (velocidade média dos veículos)
- **Phase Duration** (duração média das fases)
- **Lane Volume** (volume por faixa)

---

## 🐛 Resolução de Problemas

### Erro: `tensorflow not found`

**Causa**: Python 3.14 ou venv com Python errado

**Solução**:
```cmd
deactivate
rmdir /s venv
py -3.11 -m venv venv
venv\Scripts\activate
pip install tensorflow
```

### Erro: `SUMO_HOME not set`

**Causa**: Variável de ambiente não configurada

**Solução**:
1. Instala SUMO
2. Adiciona `SUMO_HOME` às variáveis de ambiente
3. Reinicia terminal/VS Code

### Simulação muito lenta

**Soluções**:
- Desativa GUI (`gui = False`)
- Reduz `max_steps` ou `total_episodes`
- Usa menos carros/pedestres

### Out of Memory (RAM)

**Soluções**:
- Reduz `memory_size_max`
- Reduz `batch_size`
- Reduz `width_layers` ou `num_layers`

---

## 📚 Referências

- **SUMO**: https://www.eclipse.org/sumo/
- **TensorFlow**: https://www.tensorflow.org/
- **DDQN Paper**: Van Hasselt et al., "Deep Reinforcement Learning with Double Q-learning" (2015)

---

## 👥 Contribuidores

Projeto desenvolvido no âmbito de [Curso/Instituição].

---

## 📄 Licença

[Especificar licença se aplicável]

---

**Última atualização**: Março 2026

---

> 💡 **Dica**: Começa com treinos curtos (50 episódios) para validar que tudo funciona antes de treinos longos!
