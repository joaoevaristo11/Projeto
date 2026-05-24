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
- `requirements.txt` — dependências Python: TensorFlow, numpy, matplotlib, pandas, openpyxl.
- `sumo/` — ficheiros SUMO (rede, configuração, templates de rotas geradas).
- `models/` — diretório onde cada treino cria `model_N/` com os `.h5` guardados.
- `src/agents/` — módulo dos agentes e infra-estrutura RL:
  - `model.py` — definição das classes `TrainModel` e `TestModel` (Keras/TensorFlow).
  - `memory.py` — experiência replay buffer.
  - `intersection.py` — classe `Intersection`: construção de estado, lógica de fases e utilitários.
- `src/simulation/` — lógica de simulação / orquestração:
  - `training_simulation.py` — loop de treino (coleta de experiências, replay, atualização de target).
  - `testing_simulation.py` — loop de teste e recolha de métricas.
  - `generator.py` / `ped_generator.py` — geradores de rotas veículos/pedestres.
  - `intersection_manager.py` — fábrica de interseções, rotas, zonas pedestres.
- `src/utils/` — utilitários: configuração (`utils.py`) e visualização (`visualization.py`).
- `analysis/` — scripts de processamento pós-experimento e comparação de gráficos.

Componentes Principais (o que faz cada ficheiro)
--
- `src/agents/model.py`:
  - `TrainModel`: constrói duas redes idênticas (`model` e `model_target`), métodos de inferência (`predict_one`), treino por batch (`train_batch`) e salvar modelo (`save_model`).
  - Arquitetura: Fully connected, camada de entrada com dimensão igual a `num_states` (170), duas camadas hidden de 256 ReLU (configurável), saída linear com `num_actions` (2 para fase, 4 para duração).

- `src/agents/memory.py`:
  - Buffer FIFO simples com `add_sample()` e `get_samples(n)`. Política de amostragem: `random.sample` uniforme.
  - Observação: armazena `(state, action, reward, next_state)` (sem flag `done` porque episódios têm horizonte fixo).

- `src/agents/intersection.py`:
  - Construção do estado fixo de 170 dims: representação de células de espaço/posição de veículos, velocidades agregadas normalizadas, indicadores de peões em zonas.
  - Métodos para aplicar fases e amarelos via `traci`.

- `src/simulation/training_simulation.py`:
  - Orquestra o episódio: gera rotas, inicializa fases, recolhe estados e recompensas, armazena experiências nas memórias, executa `self._replay()` para treinar redes.
  - Implementa o update DDQN: seleção com rede principal, avaliação com target network, calcula `updates = r + gamma * Q_target(s', argmax Q_online(s'))`, atualiza só a Q do par (s,a) e treina com `train_on_batch`.

- `src/simulation/testing_simulation.py`:
  - Executa simulação em modo GREEDY (ou modo REAL/BASELINE que não usa redes) e exporta métricas e gráficos por interseção.

Arquitetura do Sistema
--
Top-level: SUMO <-> TraCI <-> Simulation (Python). A simulação instancia 4 objetos `Intersection` e usa 3 redes DDQN:

- `Model_Cell_1` controla agentes J1 e J3 (mesma política de fase).
- `Model_Cell_2` controla agentes J2 e J4.
- `Model_Duration` é uma rede separada que escolhe a duração do verde (valores discretos).

Redes Neuronais e Algoritmo (DDQN)
--
Resumo técnico:

- Algoritmo: Deep Double Q-Learning (DDQN). Implementação padrão: duas redes (online/main e target). A seleção da ação é feita pela rede online e a avaliação do Q-target é através da rede target para reduzir sobreestimação.
- Arquitetura por rede:
  - Input: `num_states = 170`
  - Hidden: `num_layers = 2`, `width_layers = 256` (configurável em `config/training_settings.ini`).
  - Output: `num_actions_phase = 2` (phase networks) ou `num_actions_duration = 4` (duration network).
  - Função de perda: Huber loss (reduz sensibilidade a outliers).
  - Otimizador: Adam (learning_rate = 0.0001).

Hiperparâmetros (valores por defeito em `config/training_settings.ini`):

- `total_episodes = 300`
- `max_steps = 3600` (1h simulação)
- `gamma = 0.90`
- `batch_size = 128`
- `training_epochs = 50` (iterações de replay por episódio)
- `memory_size_min = 600`, `memory_size_max = 100000`
- `learning_rate = 0.0001`

Detalhes da atualização (código em `src/simulation/training_simulation.py`):

1. Amostrar mini-batch de transições: (s, a, r, s').
2. Computar `q_next_online = Q_online(s')` e `next_actions = argmax(q_next_online, axis=1)`.
3. Computar `q_next_target = Q_target(s')` e selecionar `selected_q_next = q_next_target[range, next_actions]`.
4. Targets: `y = r + gamma * selected_q_next`.
5. Substituir apenas os Q-values das ações tomadas em `q_s_a` por `y` e treinar `train_on_batch(states, targets)`.

Estado, Ações e Recompensa
--
Estado (`get_state` em `src/agents/intersection.py`): vetor fixo de 170 elementos composto por:

- 164 features base: marcação binária de presença por células espaciais, velocidades agregadas normalizadas, informação de peões em zonas.
- 2 features: one-hot da ação anterior (fase) — isto introduz histórico explícito da ação anterior.
- 4 features: ocupação média das faixas de entrada (padding até 4 entradas).

Ações:

- Fase (por decisão): 2 ações — `0 = NS green`, `1 = EW green`.
- Duração (por decisão): 4 ações — índices mapeados para `DURATION_VALUES = [8, 16, 24, 32]` segundos.

Recompensa (em `training_simulation.py`): combinação linear:

`reward = Pveh * (old_total_wait - current_total_wait) + Pped * (old_ped_wait - ped_wait)`

com `Pveh = 0.5` e `Pped = 0.5` por defeito. Interpretação: positivo se as esperas diminuem.

Fluxo de Treino (resumido)
--

1. Warm-up: 3 episódios com epsilon=1.0 sem treino (coleção inicial de experiências).
2. Para cada episódio (1..300):
   - Gerar ficheiros de rotas de veículos e peões (seed = episode).
   - Executar a simulação por `max_steps` passos, a cada decisão recolher estado e reward e armazenar amostras nas memórias.
   - No final do episódio, executar `training_epochs` repetições de `_replay()` para cada uma das 3 redes.
   - Após treino, copiar pesos da rede online para a target (sincronização completa).
3. Guardar modelos em `models/model_N/Trained_Cell_1.h5`, etc.

Fluxo de Teste
--

1. Em `testing_main.py`, prepara caminho de teste (`models/model_N/test_seed`).
2. Se `network` for `REAL/BASELINE/FIXED`, executa regras heurísticas; caso contrário carrega `Trained_Cell_1.h5`, `Trained_Cell_2.h5` e `Trained_Duration.h5`.
3. Executa simulação com política greedy (argmax) e recolhe métricas por interseção: filas, tempos médios de espera, velocidades, logs de durações por fase.

Como executar (ambiente e passos)
--
Requisitos

- Python 3.10+ com TensorFlow >= 2.10 (recomendado). Ver `requirements.txt`.
- SUMO (definir `SUMO_HOME` no ambiente e instalar a versão compatível). Instruções do SUMO: https://www.eclipse.org/sumo/

Instalação rápida (Windows / PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
```

Configurar SUMO (exemplo):

```powershell
setx SUMO_HOME "C:\\Program Files (x86)\\Eclipse\\Sumo"
```

Treino

```bash
python training_main.py --config config/training_settings.ini
```

Isto irá criar uma nova pasta `models/model_<N>/` com os `*.h5` e logs/plots.

Teste

```bash
python testing_main.py --config config/testing_settings.ini
```

Observações de execução
- Se estiveres em Windows e tens múltiplas versões de Python, usa `py -3.x` conforme necessário.
- O SUMO deve estar instalado e `SUMO_HOME` configurado antes de correr qualquer simulação.

Formato de ficheiros de output
--
- `models/model_N/Trained_Cell_1.h5` — Keras HDF5 do modelo de fase
- `models/model_N/Trained_Cell_2.h5` — idem
- `models/model_N/Trained_Duration.h5` — modelo de duração
- `models/model_N/*.txt` e `plot_*.png` — métricas e gráficos guardados por `Visualization`.

Análise e Visualização
--
- O diretório `analysis/` contém scripts para agregar resultados em Excel e gerar comparações gráficas entre estratégias (e.g., `graphics_comparation.py`).
- `src/utils/visualization.py` gera `.txt` com séries temporais e `.png` para cada métrica.

Limitações conhecidas e Sugestões de Melhoria
--
1. Replay Buffer não inclui flag `done` (terminal). Neste cenário de horizonte fixo isto é aceitável, mas para maior generalidade e correção convém armazenar `(state, action, reward, next_state, done)` e tratar `done` no cálculo de target: `y = r` se `done` else `r + gamma * ...`.
2. A codificação do estado inclui a `action` anterior (2 dims). Isto pode ser intencional para dar contexto, mas distorce a natureza Markoviana do estado. Avaliar remover ou transformar para histórico limitado.
3. Epsilon decai até 0.0 ao final dos episódios — recomenda-se manter um mínimo (`epsilon_min`, ex. 0.05) para evitar convergência demasiado prematura.
4. A atualização do target network é feita após todas as `training_epochs` do episódio; actualizar a cada N passos ou episódios com uma frequência ajustável pode melhorar estabilidade.
5. Recompensa pondera veículos e peões 50/50. Considerar pesos proporcionais ao volume ou multi-objetivo com Pareto/frontier.

Contribuição
--
- Para contribuir, cria um fork, faz uma branch com o teu feature/bugfix e submete um Pull Request com descrição clara.
- Para mudanças que afectem treino ou arquitetura de rede, inclui experimentos e logs comparativos.

Contacto
--
- Autor / Equipa do projeto: ver metadados do repositório (ou contacta quem te passou este código).

Licença
--
- Inclui aqui a licença do projeto se aplicável (MIT/BSD/Proprietary). Se não estiver definida, adiciona um ficheiro `LICENSE`.

Notas finais
--
Este README documenta de forma completa a arquitetura, decisões de design e fluxo de treino/teste do projeto. Se quiseres, posso também:

- Gerar um ficheiro `README_brief.md` em inglês mais curto para apresentações.
- Criar um notebook com visualizações de um `model_N/test_*` salvo.
- Aplicar as melhorias sugeridas (flag `done`, epsilon_min, atualização target mais frequente) e executar um pequeno teste local.

-- Fim do README completo.
