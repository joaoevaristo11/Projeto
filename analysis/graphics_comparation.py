import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ler ficheiros Excel
excel_1 = pd.read_excel(r'valores_inteligente.xlsx')
excel_2 = pd.read_excel(r'valores_real.xlsx')

name_1 = 'Inteligente'
name_2 = 'Real'

# Diretoria de destino
diretoria = r'./analysis/comparacao_graficos'
os.makedirs(diretoria, exist_ok=True)

# Colunas com índice 1..4 (C1..C4) 
metrics_reward     = ['reward_1','reward_2','reward_3','reward_4']
metrics_queue      = ['queue_1','queue_2','queue_3','queue_4']
metrics_ped        = ['ped_halting_1','ped_halting_2','ped_halting_3','ped_halting_4']
metrics_speed      = ['speed_med_1','speed_med_2','speed_med_3','speed_med_4']
metrics_wt         = ['avg_wt_1','avg_wt_2','avg_wt_3','avg_wt_4']
metrics_phase_time = ['avg_phase_time_1','avg_phase_time_2','avg_phase_time_3','avg_phase_time_4']
metric_lane_volume = ['lane_volume_1']

# ── Reward ─────────────────────────────────────────────────────────────────────
for i, col in enumerate(metrics_reward, start=1):   # FIX: start=1 → C1..C4
    plt.figure()
    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    plt.xlabel('Episodes', fontsize=18)
    plt.ylabel(f'Reward at Intersection C{i}', fontsize=18)
    plt.legend(fontsize=14, loc='lower left')
    plt.grid(True)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'comparacao_reward_C{i}.png'
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()

# ── Queue ──────────────────────────────────────────────────────────────────────
for i, col in enumerate(metrics_queue, start=1):
    plt.figure()
    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    plt.xlabel('Time (s)', fontsize=18)
    plt.ylabel(f'Halting at Intersection C{i} (vehicles)', fontsize=18)
    plt.title(f'Halting Vehicles at Intersection C{i}', fontsize=16)
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.ylim(0, 90)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'comparacao_queue_C{i}.png'
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()

# ── Pedestrian Halting ─────────────────────────────────────────────────────────
for i, col in enumerate(metrics_ped, start=1):
    plt.figure()
    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    plt.xlabel('Time (s)', fontsize=18)
    plt.ylabel(f'Halting at Intersection C{i} (pedestrians)', fontsize=18)
    plt.title(f'Halting Pedestrians at Intersection C{i}', fontsize=18)
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.ylim(0, 40)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'comparacao_halt_ped_C{i}.png'
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()

# ── Speed ──────────────────────────────────────────────────────────────────────
for i, col in enumerate(metrics_speed, start=1):
    plt.figure()
    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    plt.xlabel('Time (s)', fontsize=18)
    plt.ylabel('Vehicles speed (m/s)', fontsize=18)
    plt.title(f'Average Speed in C{i}')
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'comparacao_speed_C{i}.png'
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()

# ── Waiting Time ───────────────────────────────────────────────────────────────
for i, col in enumerate(metrics_wt, start=1):
    plt.figure()
    plt.plot(excel_1[col], label=name_1)
    plt.plot(excel_2[col], label=name_2)
    plt.xlabel('Time (Minutes)', fontsize=18)
    plt.ylabel('Time (seconds)', fontsize=18)
    plt.title(f'Average Waiting Time in C{i}')
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'arrival_C{i}.png'     # FIX: era arrival_0..3, agora arrival_C1..C4
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()

# ── Phase Time ─────────────────────────────────────────────────────────────────
for i, col in enumerate(metrics_phase_time, start=1):
    plt.figure()
    phases = list(range(len(excel_1)))
    plt.bar(phases, excel_1[col], color='skyblue', label=name_1)
    plt.bar(phases, excel_2[col], color='green',   label=name_2)
    plt.xlabel('NS, N, S, NS_L, WE, W, E, WE_L, Ped', fontsize=18)
    plt.ylabel('Phase Time (seconds)', fontsize=18)
    plt.title(f'Average Phase Time in C{i}')
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.ylim(0, 60)
    plt.xlim(1, 9)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'phaseTime_C{i}.png'   # FIX: era phaseTime_0..3, agora phaseTime_C1..C4
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()

# ── Lane Volume ────────────────────────────────────────────────────────────────
for i, col in enumerate(metric_lane_volume, start=1):
    plt.figure()
    phases = list(range(len(excel_1)))
    plt.bar(phases, excel_1[col], color='skyblue', label=name_1)
    plt.bar(phases, excel_2[col], color='green',   label=name_2)
    plt.xlabel('W_C0, N_C3, S_C4, N_C2, S_C2, N_C7, S_C8, E_C6', fontsize=14)
    plt.ylabel('Volume per Lane (veh/hour)', fontsize=18)
    plt.title('Volume in Lanes')
    plt.legend(fontsize=14, loc='upper right')
    plt.grid(True)
    plt.tick_params(axis='both', labelsize=16)
    nome_ficheiro = f'lanevolumes_{i}.png'
    plt.savefig(os.path.join(diretoria, nome_ficheiro), dpi=300, bbox_inches='tight')
    plt.close()