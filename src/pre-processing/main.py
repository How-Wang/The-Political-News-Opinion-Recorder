import pathlib
import pickle
import pandas as pd
from multiprocessing import Pool
from remove_space import remove_space
from replace_comma import replace_comma
from timestemp_convert import timestemp_convert
import datetime

def run_process(csv_name, save_path):
    print(f'Start processing {csv_name}')
    df = pd.read_csv(csv_name)
    df = df.dropna(subset=['title', 'article'])
    df['article'], df['space_index'] = zip(*df['article'].map(remove_space))
    df = timestemp_convert(df)
    # save_path = Path(PROCESSED_DTA_PATH) / str(csv_name).split('/')[-1]
    df.to_csv(save_path, index=False)
    print(f'Finish processing {csv_name}')



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    # yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # yesterday_str = yesterday.strftime("%Y-%m-%d")

    # start_datetime = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    parser.add_argument('--input_start_date',
                    help='enter input start date')
    args = parser.parse_args()
    start_datetime = args.input_start_date

    RAW_DATA_PATH = '/crawler/result/raw/' + start_datetime + '_news'
    PROCESSED_DTA_PATH = '../crawler/result/processed/' + start_datetime + '_news'
    RECORD_PATH = '../crawler/result/record/' + start_datetime + '_news'

    # RAW_DATA_PATH = 'test_dir'
    path = pathlib.Path(str(pathlib.Path.cwd().parent) + RAW_DATA_PATH)
    raw_file_names = list(path.iterdir())

    # with open(RECORD_PATH + '/processed_file_names.pikle', 'rb') as f:
    #     try:
    #         processed_file_names = pickle.load(f)
    #     except EOFError:
    #         processed_file_names = []

    #     files_to_process = [file_name for file_name in raw_file_names if file_name not in processed_file_names]
    #     processed_file_names += files_to_process
    
    # with open(RECORD_PATH + '/processed_file_names.pikle', 'wb') as f: 
    #     pickle.dump(processed_file_names, f)
    
    
    # with Pool(len(files_to_process)) as p:
    #     p.map(run_process, files_to_process)

    for file_name in raw_file_names:
        # print(str(file_name).split('\\')[-1])
        # save_path = PROCESSED_DTA_PATH+ '/' + str(file_name).split('/')[-1] # for MAC
        save_path = PROCESSED_DTA_PATH+ '\\' + str(file_name).split('\\')[-1] # for WINDOWS
        pathlib.Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        run_process(file_name, save_path)