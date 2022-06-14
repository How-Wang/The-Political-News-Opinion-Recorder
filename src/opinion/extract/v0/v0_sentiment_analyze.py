def top(file_full_name, n_dict_path, p_dict_path):
    news_df = pd.read_csv(file_full_name)
    negative_list = []
    f = open(n_dict_path, encoding='utf16')
    for line in f.readlines():
        negative_list.append(line.replace('\n',''))

    positive_list = []
    f = open(p_dict_path, encoding='utf16')
    for line in f.readlines():
        positive_list.append(line.replace('\n',''))

    all_opinions_list = []
    for i in range(len(news_df)):
        opinions_list = ast.literal_eval(news_df.iloc[i]["all_opinions_after_cluster"])
        for j in range(len(opinions_list)):
            n_score = 0
            p_score = 0
            n_list = []
            p_list = []
            for nw in negative_list:
                if nw in opinions_list[j]['opinion'] and nw != "":
                    n_score += 1
                    n_list.append(nw)
            for pw in positive_list:
                if pw in opinions_list[j]['opinion'] and pw != "":
                    p_score += 1
                    p_list.append(pw)
            opinions_list[j]['negative_score'] = n_score
            opinions_list[j]['positive_score'] = p_score
            opinions_list[j]['negative_list'] = n_list
            opinions_list[j]['positive_list'] = p_list
        all_opinions_list.append(opinions_list)
    news_df["all_opinions_after_cluster"] = all_opinions_list
    
    return news_df

if __name__ == '__main__':
    import pandas as pd
    import ast
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                       default='./result/total_opinions.csv',
                       help='enter input news data csv file path')
    
    parser.add_argument('--input_negative_path',
                       default='../opinion/extract/result/setiment_dict/NTUSD_negative_unicode.txt',
                       help='enter negative file path')

    parser.add_argument('--input_positive_path',
                    default='../opinion/extract/result/setiment_dict/NTUSD_positive_unicode.txt',
                    help='enter positive file path')

    args = parser.parse_args()
    file_full_name = args.input_news_file_path
    n_dict_path = args.input_negative_path
    p_dict_path = args.input_positive_path

    news_df = top(file_full_name, n_dict_path, p_dict_path)
    news_df.to_csv(file_full_name, index=False)
    

