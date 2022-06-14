from pathlib import Path
import pickle
import os

TOTAL_OPINION_PATH = '../../../result/opinion/v0_combine_opinions_and_cluster/v0_Total_Opinion'

DATA_PATH = '../../../matrix/opinion/validated_py/v0_data'
FORMATTED_PATH = '../../../matrix/opinion/validated_py/v0_formatted'
VISUALIZATION_PATH = '../../../matrix/opinion/validated_py/v0_visualization'

def run_validate(csv_name):
    file_name = str(csv_name).split('/')[-1]
    print(f'Start processing {file_name}') 
    print(f'python3  validated.py --input_total_opinion_path {csv_name} --output_data_path {DATA_PATH}/{file_name} --output_visualize_path {VISUALIZATION_PATH}/{file_name} --output_formatted_path {FORMATTED_PATH}/{file_name}')
    os.system(f'python3  validated.py --input_total_opinion_path {csv_name} --output_data_path {DATA_PATH}/{file_name} --output_visualize_path {VISUALIZATION_PATH}/{file_name} --output_formatted_path {FORMATTED_PATH}/{file_name}')
    print(f'Finish processing {file_name}')

if __name__ == "__main__":
    path = Path(TOTAL_OPINION_PATH)    
    raw_file_names = list(path.iterdir())
    # print(raw_file_names)

    for csv in raw_file_names:
        run_validate(csv)