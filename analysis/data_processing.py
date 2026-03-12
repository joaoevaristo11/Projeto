import os
import numpy as np
from openpyxl import Workbook, load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import column_index_from_string
from openpyxl.chart.series import SeriesLabel

# CONFIGURAÇÕES
models = {'Estratégia 4': r'E:\GGALVAO\BOLSA\Trabalhos\2_NN_2_cells_DQN\TLCS\models\model_8'}

test_dirs = ['test_5000', 'test_10000', 'test_10003']
excel_file = r'E:\GGALVAO\BOLSA\Trabalhos\2_NN_2_cells_DQN\TLCS\models\model_8\valores_treino_teste_5.xlsx'

column_mapping = {
    # 9 COLUNAS (5 originais + 4 novas: A a I). A próxima métrica começa em K (J é vazia).
    'reward': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],

    # 9 COLUNAS (K a S). (T é vazia)
    'queue': ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'],

    # 9 COLUNAS (U a AC). (AD é vazia)
    'ped_halting': ['U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC'],

    # 9 COLUNAS (AE a AM). (AN é vazia)
    'speed_med': ['AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM'],

    # 9 COLUNAS (AO a AW). (AX é vazia)
    'avg_wt': ['AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW'],

    # 9 COLUNAS (AY a BG). (BH é vazia)
    'avg_phase_time': ['AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG'],

    # 1 COLUNA (BI).
    'lane_volume': ['BI']
}

reward_files = [f'reward_C{i}.txt' for i in range(1, 5)]  # 4 interseções: C1, C2, C3, C4
queue_files = [f'Queue_{i}.txt' for i in range(1, 5)]
ped_halting_files = [f'Pedestrian Halting C{i}.txt' for i in range(1, 5)]
speed_med_files = [f'Average Vehicle Speed C{i}.txt' for i in range(1, 5)]
wt_med_files = [f'Average Waiting Time C{i}.txt' for i in range(1, 5)]
pT_med_files = [f'Average Phase Time in C{i}.txt' for i in range(1, 5)]
extra_files = {f'Lane Volume.txt'}

# Inicializar Excel
wb = Workbook()
for sheet in models.keys():
    wb.create_sheet(title=sheet)
wb.remove(wb['Sheet'])
wb.save(excel_file)

def read_file_lines(path):
    with open(path, 'r') as f:
        return [float(line.strip()) for line in f if line.strip()]

def media_entre_testes(base_path, ficheiro_nome):
    valores = []
    for test_dir in test_dirs:
        path = os.path.join(base_path, test_dir, ficheiro_nome)
        linhas = read_file_lines(path)
        valores.append(linhas)
    return np.mean(np.array(valores), axis=0).tolist()

# Processar cada modelo
for sheet_name, model_path in models.items():
    print(f"🔄 A processar: {sheet_name}...")

    wb = load_workbook(excel_file)
    sheet = wb[sheet_name]

    for tipo, colunas in column_mapping.items():
        if isinstance(colunas, list):
            for i, col in enumerate(colunas):
                sheet[f'{col}1'] = f'{tipo}_{i}'
        else:
            sheet[f'{colunas}1'] = tipo

    for idx, ficheiro in enumerate(reward_files):
        path = os.path.join(model_path, ficheiro)
        valores = read_file_lines(path)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['reward'][idx]
            sheet[f'{col}{row_idx}'] = valor

    for idx, ficheiro in enumerate(queue_files):
        valores = media_entre_testes(model_path, ficheiro)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['queue'][idx]
            sheet[f'{col}{row_idx}'] = valor

    for idx, ficheiro in enumerate(ped_halting_files):
        valores = media_entre_testes(model_path, ficheiro)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['ped_halting'][idx]
            sheet[f'{col}{row_idx}'] = valor

    for idx, ficheiro in enumerate(speed_med_files):
        valores = media_entre_testes(model_path, ficheiro)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['speed_med'][idx]
            sheet[f'{col}{row_idx}'] = valor

    for idx, ficheiro in enumerate(wt_med_files):
        valores = media_entre_testes(model_path, ficheiro)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['avg_wt'][idx]
            sheet[f'{col}{row_idx}'] = valor

    for idx, ficheiro in enumerate(pT_med_files):
        valores = media_entre_testes(model_path, ficheiro)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['avg_phase_time'][idx]
            sheet[f'{col}{row_idx}'] = valor

    for idx, ficheiro in enumerate(extra_files):
        valores = media_entre_testes(model_path, ficheiro)
        for row_idx, valor in enumerate(valores, 2):
            col = column_mapping['lane_volume'][idx]
            sheet[f'{col}{row_idx}'] = valor

    wb.save(excel_file)

wb.save(excel_file)
print(f"\n✅ Valores calculados e gráficos guardados em:\n{excel_file}")
