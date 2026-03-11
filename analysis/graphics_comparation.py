import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ler ficheiros Excel
excel_1 = pd.read_excel(r'E:\GGALVAO\BOLSA\Trabalhos\2_NN_2_cells_DQN\TLCS\2_NN\model_8\valores_treino_teste_5.xlsx')
excel_2 = pd.read_excel(r'E:\GGALVAO\BOLSA\Trabalhos\2_NN_2_cells_DQN\TLCS\models\model_8\valores_treino_teste_5.xlsx')
#excel_3 = pd.read_excel(r'E:\GGALVAO\BOLSA\Trabalhos\RedeNeuronal_2_cells\TLCS\models\model_1\valores_treino_teste_1.xlsx')

name_1 = '2 NN - High Radial In'
name_2 = '2 NN - High Radial In - Sapa adj'
#name_3 = 'More Control Circular/Radial'

# Diretoria de destino
diretoria = r'C:\Users\ggalvao\Desktop\9_intersections\5_5_sapa_adj'
os.makedirs(diretoria, exist_ok=True)

# Lista de colunas que queres comparar
metrics_reward = ['reward_0', 'reward_1', 'reward_2', 'reward_3', 'reward_4', 'reward_5', 'reward_6', 'reward_7', 'reward_8']

metrics_queue = ['queue_0', 'queue_1', 'queue_2', 'queue_3', 'queue_4', 'queue_5', 'queue_6', 'queue_7', 'queue_8']

metrics_ped = ['ped_halting_0', 'ped_halting_1', 'ped_halting_2', 'ped_halting_3', 'ped_halting_4', 'ped_halting_5', 'ped_halting_6', 'ped_halting_7', 'ped_halting_8']

metrics_speed = ['speed_med_0', 'speed_med_1', 'speed_med_2', 'speed_med_3', 'speed_med_4', 'speed_med_5', 'speed_med_6', 'speed_med_7', 'speed_med_8']

metrics_wt = ['avg_wt_0', 'avg_wt_1','avg_wt_2', 'avg_wt_3','avg_wt_4', 'avg_wt_5', 'avg_wt_6', 'avg_wt_7', 'avg_wt_8',]

metrics_phase_time = ['avg_phase_time_0', 'avg_phase_time_1', 'avg_phase_time_2', 'avg_phase_time_3', 'avg_phase_time_4', 'avg_phase_time_5', 'avg_phase_time_6', 'avg_phase_time_7', 'avg_phase_time_8', ]

metric_lane_volume = ['lane_volume_0']

# Loop sobre cada coluna
for i, col in enumerate(metrics_reward):
    plt.figure()  # cria uma nova figura para cada gráfico

    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    #plt.plot(excel_3[col],color='yellow', label=name_3)
    plt.xlabel('Episodes', fontsize=18)
    plt.ylabel(f'Reward at Intersection C{i}', fontsize=18)
    #plt.title(f'Reward at Intersection C{i}', fontsize=16)  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='lower left')
    plt.grid(True)

    #plt.ylim(0, 55)
    plt.tick_params(axis='both', labelsize=16)

    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'comparacao_reward_C{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()

for i, col in enumerate(metrics_queue):
    plt.figure()  # cria uma nova figura para cada gráfico

    plt.plot(excel_1[col],label= name_1)
    plt.plot(excel_2[col], label=name_2)
    #plt.plot(excel_3[col], color='yellow', label=name_3)
    plt.xlabel('Time (s)', fontsize=18)
    plt.ylabel(f'Halting at Intersection C{i} (vehicles)', fontsize=18)
    plt.title(f'Halting Vehicles at Intersection C{i}', fontsize=16)  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)

    plt.ylim(0, 90)
    plt.tick_params(axis='both', labelsize=16)

    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'comparacao_queue_C{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()

for i, col in enumerate(metrics_ped):
    plt.figure()  # cria uma nova figura para cada gráfico

    plt.plot(excel_1[col],label= name_1)
    plt.plot(excel_2[col],label= name_2)
    #plt.plot(excel_3[col], color='yellow', label=name_3)
    plt.xlabel('Time (s)', fontsize=18)
    plt.ylabel(f'Halting at Intersection C{i} (pedestrians)', fontsize=18)
    plt.title(f'Halting Pedestrians at Intersection C{i}', fontsize=18)  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)

    plt.ylim(0, 40)
    plt.tick_params(axis='both', labelsize=16)

    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'comparacao_halt_ped_C{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()

for i, col in enumerate(metrics_speed):
    plt.figure()  # cria uma nova figura para cada gráfico

    plt.plot(excel_1[col],label= name_1)
    plt.plot(excel_2[col], label=name_2)
    #plt.plot(excel_3[col], color='yellow',label=name_3)
    plt.xlabel('Time (s)', fontsize=18)
    plt.ylabel('Vehicles speed (m/s)', fontsize=18)
    plt.title(f'Average Speed in C{i}')  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.tick_params(axis='both', labelsize=16)

    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'comparacao_speed_C{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()

for i, col in enumerate(metrics_wt):

    plt.figure()  # cria uma nova figura para cada gráfico

    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    #plt.plot(excel_3[col], color='yellow', label=name_3)
    plt.xlabel('Time (Minutes)', fontsize=18)
    plt.ylabel('Time (seconds)', fontsize=18)
    plt.title(f'Average Waiting Time in C{i}')  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.tick_params(axis='both', labelsize=16)
    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'arrival_{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()

for i, col in enumerate(metrics_phase_time):

    plt.figure()  # cria uma nova figura para cada gráfico

    phases = list(range(len(excel_1)))

    plt.bar(phases, excel_1[col], color='skyblue', label=name_1)
    plt.bar(phases, excel_2[col], color='green', label=name_2)
    #plt.plot(excel_3[col], color='yellow', label=name_3)

    plt.xlabel('NS, N, S, NS_L, WE, W, E, WE_L, Ped', fontsize=18)
    plt.ylabel('Phase Time (seconds)', fontsize=18)
    plt.title(f'Average Phase Time in C{i}')  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.ylim(0, 60)
    plt.xlim(1, 9)
    plt.tick_params(axis='both', labelsize=16)

    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'phaseTime_{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()

for i, col in enumerate(metric_lane_volume):

    plt.figure()  # cria uma nova figura para cada gráfico

    phases = list(range(len(excel_1)))
    Volume_Lanes = ['W_TL0', 'N_TL3', 'S_TL4', 'N_TL2', 'S_TL2', 'N_TL7', 'S_TL8', 'E_TL6']
    #phases = list(range(8))

    plt.bar(phases, excel_1[col], color='skyblue', label=name_1)
    plt.bar(phases, excel_2[col], color='green', label=name_2)
    #plt.xticks(phases, Volume_Lanes, rotation=45, ha='right')
    #plt.plot(excel_3[col], color='yellow', label=name_3)

    plt.xlabel('W_C0, N_C3, S_C4, N_C2, S_C2, N_C7, S_C8, E_C6', fontsize=14)
    plt.ylabel('Volume per Lane (veh/hour)', fontsize=18)
    plt.title(f'Volume in Lanes')  # Usamos C0, C1, etc.
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    #plt.ylim(0, 60)
    #plt.xlim(1, 9)
    plt.tick_params(axis='both', labelsize=16)

    # Nome do ficheiro com base no índice (C0, C1, ...)
    nome_ficheiro = f'lanevolumes_{i}.png'
    path = os.path.join(diretoria, nome_ficheiro)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()



