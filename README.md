TLCS — Traffic Light Control System (DDQN)

Resumo profissional e técnico do projeto.

Índice
--
- Visão Geral
- Destaques e Objetivos
- Estrutura do Repositório
- Componentes Principais (ficheiros e responsabilidades)
- Arquitetura do Sistema
- Redes Neuronais e Algoritmo (DDQN)
- Estado, Ações e Recompensa
- Fluxo de Treino e Teste (passo-a-passo)
- Instruções de Execução (instalação, treino, teste)
- Formato de Ficheiros (models, logs, outputs)
- Análise e Visualização
- Limitações conhecidas e Sugestões de Melhoria
- Contribuição e Contacto

Visão Geral
--
Este projeto implementa um sistema multi-agente de controlo de semáforos urbano usando Deep Reinforcement Learning (DDQN). O ambiente de simulação é o SUMO (Simulation of Urban Mobility) e o objetivo é reduzir tempos de espera e filas de veículos e peões em quatro interseções reais modeladas (J1..J4).

Destaques e Objetivos
--
- Controlar 4 interseções numa topologia 2x2 com agentes locais.
- Dividir o problema em três redes DDQN: duas redes de "fase" (Cell_1 e Cell_2) e uma rede de "duração" partilhada.
- Aprender políticas que escolhem fase (NS/EW) e duração do verde (8s,16s,24s,32s).
- Usar Experience Replay, Target Network e Huber loss para treino estável.

Estrutura do Repositório
--
Raiz do projeto (principais ficheiros/dirs):

- `training_main.py` — script de treino principal (config usa `config/training_settings.ini`).
- `testing_main.py` — script de teste/avaliação (config usa `config/testing_settings.ini`).
TLCS — Traffic Light Control System (DDQN)

**Resumo**
Este repositório contém uma implementação multi-agente para controlo adaptativo de semáforos urbanos baseada em Deep Reinforcement Learning (DDQN). A simulação usa SUMO (TraCI) para modelar tráfego de veículos e peões em quatro cruzamentos; o objetivo é minimizar tempos de espera, filas e interrupções, aprendendo políticas de fase e duração.

**Índice**
- **Visão Geral**
- **Principais Características**
- **Estrutura do Repositório**
- **Instalação & Requisitos**
- **Configuração**
- **Como Executar**
- **Arquitetura e Implementação**
- **Redes Neuronais & Algoritmo (DDQN)**
- **Estado, Ações e Recompensa**
- **Outputs e Formatos**
- **Análise, Resultados e Visualização**
- **Limitações & Melhorias Recomendadas**
- **Contribuir**
- **Licença & Contacto**

**Visão Geral**
- Objetivo: aprender políticas locais para gerir fases e durações de semáforos que reduzam espera de veículos e peões.
- Abordagem: três redes DDQN (duas para seleção de fase, uma para seleção de duração) com Experience Replay e target networks.

**Principais Características**
- Multi-agente: 4 agentes distribuídos (J1..J4) partilham 3 modelos (Cell_1, Cell_2, Duration).
- Separação de decisões: fase (NS/EW) e duração do verde (discretizada).
- Implementação em TensorFlow/Keras com Huber loss e Adam optimizer.
- Integração com SUMO via TraCI para simulações realistas.

**Estrutura do Repositório**
- **[training_main.py](training_main.py)**: script principal para treino (usa `config/training_settings.ini`).
- **[testing_main.py](testing_main.py)**: script de teste/avaliação (usa `config/testing_settings.ini`).
- **[requirements.txt](requirements.txt)**: dependências Python.
- **config/**: ficheiros de configuração (`training_settings.ini`, `testing_settings.ini`).
- **src/agents/**: implementação das redes e do replay buffer ([src/agents/model.py](src/agents/model.py)).
- **src/simulation/**: orquestração das simulações de treino e teste ([src/simulation/training_simulation.py](src/simulation/training_simulation.py)).
- **src/utils/**: utilitários e visualização.
- **models/**: modelos treinados e pastas com logs/plots.
- **sumo/**: rede SUMO, rotas e ficheiros de configuração.
- **analysis/**: scripts de pós-processamento e comparação de resultados.

**Instalação & Requisitos**
- Sistema: Windows / Linux (SUMO necessário para simulação).
- Python: 3.10+.
- Dependências: ver **[requirements.txt](requirements.txt)** (TensorFlow >= 2.10, numpy, pandas, matplotlib, openpyxl).
- SUMO: instalar e configurar `SUMO_HOME` (https://www.eclipse.org/sumo/). `traci` é usado para comunicação com o simulador.

Instalação rápida (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configurar SUMO (exemplo Windows):

```powershell
setx SUMO_HOME "C:\Program Files (x86)\Eclipse\Sumo"
```

**Configuração**
- Os ficheiros de configuração principais estão em **config/**:
  - **[config/training_settings.ini](config/training_settings.ini)** — hiperparâmetros de treino, paths, memória, rede.
  - **[config/testing_settings.ini](config/testing_settings.ini)** — parâmetros de teste e paths.

Ver e ajustar: número de episódios, tamanho do batch, dimensão das redes (`num_layers`, `width_layers`), seeds e paths de saída.

**Como Executar**
- Treino (exemplo):

```bash
python training_main.py --config config/training_settings.ini
```

- Teste/avaliação (exemplo):

```bash
python testing_main.py --config config/testing_settings.ini
```

**Arquitetura e Implementação**
- Loop principal de treino está em **[src/simulation/training_simulation.py](src/simulation/training_simulation.py)**. Aqui ocorre:
  - geração de rotas (vehicles + pedestrians), execução passo-a-passo com `traci`;
  - recolha de estados e recompensas por interseção;
  - armazenamento de transições nas memórias e execução do _replay_ para treino das redes;
  - sincronização dos pesos do `model` para o `model_target`.

- Modelos (ver **[src/agents/model.py](src/agents/model.py)**):
  - `TrainModel`: constrói `model` e `model_target` com camadas Dense (ReLU) e saída linear;
  - arquitetura padrão: input dim = 170 (ou 176 para alguns cruzamentos), `num_layers = 2`, `width_layers = 256`;
  - perda: Huber; otimizador: Adam.

**Redes Neuronais & Algoritmo (DDQN)**
- Implementação Double DQN:
  - Ação selecionada por `Q_online` (argmax), valor avaliado por `Q_target` para reduzir sobreestimação.
  - Atualização dos alvos respetivos aos pares (s, a) com `y = r + gamma * Q_target(s', argmax Q_online(s'))`.
  - Treino por batch com `train_on_batch` e repetição de `_replay()` por `training_epochs` no final do episódio.

Hiperparâmetros por defeito (ver **config/**):
- `total_episodes`, `max_steps`, `gamma`, `batch_size`, `training_epochs`, `memory_size_min/max`, `learning_rate`.

**Estado, Ações e Recompensa**
- Estado: vetor fixo (170 ou 176 dimensões) com representação espacial de veículos, velocidades normalizadas, indicadores de peões e histórico curto (ação anterior).
- Ações:
  - Fase: 2 ações — `0 = NS`, `1 = EW`.
  - Duração: 4 ações — mapeadas para valores discretos (ex.: [8, 16, 24, 32]s).
- Recompensa: combinação linear entre redução de espera de veículos e peões:

```
reward = Pveh * (old_total_wait - current_total_wait) + Pped * (old_ped_wait - ped_wait)
```

com `Pveh = 0.5` e `Pped = 0.5` por omissão (ajustável em código/config).

**Outputs e Formatos**
- Modelos guardados: `models/model_<N>/Trained_Cell_1.h5`, `Trained_Cell_2.h5`, `Trained_Duration.h5`.
- Métricas/plots: ficheiros `.txt` e `.png` gerados por `Visualization` para recompensas, perda, filas, velocidades e tempos de espera.

**Análise, Resultados e Visualização**
- Use os scripts em **analysis/** para agregar resultados e gerar comparações.
- Exemplos: gráficos de reward por episódio (`Reward_C1.txt`), MSE loss por modelo e barras de tempo médio de fase.

**Limitações & Melhorias Recomendadas**
- O buffer de replay não inclui flag `done`; para episódios com terminação variável recomendo adicionar `done` e tratar corretamente o target.
- Introduzir `epsilon_min` para exploração persistente (evitar epsilon → 0).
- Atualizar target network periodicamente (por passos) em vez de sincronizar só no fim do episódio pode melhorar estabilidade.
- Considerar normalização/standardização mais robusta do estado e arquitetura com camadas residuais ou regularização (dropout / weight decay) se overfitting for observado.

**Contribuir**
- Fork → branch feature → Pull Request com descrição e resultados experimentais.

**Licença & Contacto**
- Adicione um ficheiro `LICENSE` com a licença desejada (ex.: MIT). Para contacto, consulte os metadados do repositório ou o autor original.

---

Se quiseres, prossigo com:
- Gerar um resumo em inglês para apresentações;
- Adicionar um notebook de análise com um exemplo de `models/model_<N>/`;
- Implementar melhorias rápidas (flag `done`, `epsilon_min`, atualização do target por passos) e testar num episódio.

Fim.

