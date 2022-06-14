def top(dir_path):
    # get all files under yesterday news
    onlyfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    # create empty dataframe
    column_names = ["title","article","url","company","category","reporter","space_index","datetime","year","month","day","hour","minute"]
    concate_df = pd.DataFrame(columns = column_names)

    # concate files one by one
    for i in range(len(onlyfiles)):
        temp_df = pd.read_csv(dir_path + onlyfiles[i])
        # don't have loss value, concate
        if not temp_df['datetime'].isnull().values.any():
            concate_df = pd.concat([concate_df, temp_df], ignore_index=True)

    return concate_df

if __name__=='__main__':
    import pandas as pd
    import datetime
    from os import listdir
    from os.path import isfile, join
    # yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # yesterday_str = yesterday.strftime("%Y-%m-%d")

    # start_datetime = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_start_date',
                    help='enter input start date')
    args = parser.parse_args()
    start_datetime = args.input_start_date

    dir_path = '../crawler/result/processed/'+ start_datetime +'_news/'

    concate_df = top(dir_path)
    concate_df.to_csv(dir_path + '/' + start_datetime + '-news.csv' , index=False)

