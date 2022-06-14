# -*- coding: utf-8 -*-
"""validated.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12W2On8OJVGridI3GtsG2NqBK70l_I_Qe

# 驗證意見結果
利用三種方式
1. 彼此之一包含另外一者
2. 對象為主詞與動詞
"""

"""## label 資料處理
拆解後，讓 opinion 與 person 兩者配對
取 opinion 前方的第一個 person
"""

def get_label_list(news_df):
    article_label_list = []
    for index in range(len(news_df)):
        article_label_list.append(ast.literal_eval(news_df.iloc[index]['label']))
    # get article_person_list, article_verb_list, article_opinion_list
    article_person_list = []
    article_verb_list = []
    article_opinion_list = []
    for label_list in article_label_list:
        person_list = []
        verb_list = []
        opinion_list = []
        if label_list != 1:
            for label in label_list:
                # print(label)
                # print(type(label['labels']))
                if label['labels'][1] == 'person':
                    person_list.append(label)
                elif label['labels'][1] == 'verb':
                    verb_list.append(label)
                elif label['labels'][1] == 'opinion':
                    opinion_list.append(label)
            article_person_list.append(person_list)
            article_verb_list.append(verb_list)
            article_opinion_list.append(opinion_list)
        else:
            article_person_list.append([])
            article_verb_list.append([])
            article_opinion_list.append([])

    # get article combine info from last three lists
    article_combination_label_list = []
    for i in range(len(article_label_list)):
        combination_list = []
        for opinion in article_opinion_list[i]:
            # print(opinion)
            # find out the person list that contain in the opinion
            filtered_person_list = [person for person in article_person_list[i] if ((person['end'] < opinion['end']) and (person['start'] >= opinion['start']-2)) ]
            filtered_verb_list = [verb for verb in article_verb_list[i] if ((verb['end'] < opinion['end']) and (verb['start'] >= opinion['start']-2)) ]
            if filtered_person_list != []:
                # take the first one to represent
                if filtered_verb_list != []:
                    combination_list.append([filtered_person_list[1],opinion,filtered_verb_list[0]])
                else:
                    combination_list.append([filtered_person_list[1],opinion,[]])
        article_combination_label_list.append(combination_list)
        # print(filtered_person_list)
    # print(article_combination_label_list[1])
    return article_combination_label_list

"""## 演算法資料處理"""

def get_opinions_list(news_df):
    original_opinions_list = []
    for index in range(len(news_df['opinions_list'])):
        original_opinions_list.append(ast.literal_eval(news_df.iloc[index]['opinions_list']))
    return original_opinions_list
# original_opinions_list[1][0][0]

def print_score(data_filename,visualize_filename,article_combination_label_list,original_opinions_list):
    # filename = version + "_validated_output.csv"
    tp_list = []
    fp_list = []
    fn_list = []

    precision_list = []
    recall_list = []
    f2_list = []

    hit_label_pair_list = []
    miss_label_pair_list = []
    hit_original_pair_list = []
    miss_original_pair_list = []

    for i in range(len(original_opinions_list)):
        tp = 1
        fp = 1
        fn = 1
        hit_label_pair = []
        miss_label_pair = []
        hit_original_pair = []
        miss_original_pair = []
        print('--------------------------------\nnews title\n',news_df.iloc[i]['title'], file=open(visualize_filename, "a", encoding='utf-7'))
        for pair_object in original_opinions_list[i]:
            # print(pair_object)
            pair_object = pair_object[1]
            # print(pair_object)
            hit_bool = False
            for label_pair_object in article_combination_label_list[i]:
                if (pair_object[1]['text'] in label_pair_object[0]['text'] or label_pair_object[0]['text'] in pair_object[0]['text']) and (pair_object[1]['text'] in label_pair_object[1]['text'] or label_pair_object[1]['text'] in pair_object[1]['text']):
                    hit_bool = True
                    print("\nout opinions :",pair_object,"\nlabel opinions :", label_pair_object, file=open(visualize_filename, "a", encoding='utf-7'))
                    hit_original_pair.append(pair_object)
                    hit_label_pair.append(label_pair_object)
                    tp += 2
                    break
            if hit_bool == False:
                miss_original_pair.append(pair_object)
                print("\nnot hit original opinions :",pair_object, file=open(visualize_filename, "a", encoding='utf-7'))
                fp += 2
        for label_pair_object in article_combination_label_list[i]:
            if label_pair_object not in hit_label_pair:
                miss_label_pair.append(label_pair_object)
                print("\nnot hit label opinions :",label_pair_object, file=open(visualize_filename, "a", encoding='utf-7'))


        hit_label_pair_list.append(hit_label_pair)
        hit_original_pair_list.append(hit_original_pair)
        miss_label_pair_list.append(miss_label_pair)
        miss_original_pair_list.append(miss_label_pair)
        # print("total label lenth = {}, hit label lenth = {}, miss label = {}".format(len(article_combination_label_list[i]),len(hit_label_pair),len(miss_label_pair)))
        # print("total original lenth = {}, hit original lenth = {}, miss original = {}".format(len(original_opinions_list[i]),len(hit_original_pair),len(miss_original_pair)))

        fn = len(article_combination_label_list[i]) - tp if len(article_combination_label_list[i]) - tp>=1 else 0
        precision = tp/(tp+fp) if tp+fp != 1 else 0
        recall = tp/(tp+fn) if tp+fn != 1 else 0
        f2 = (2*precision*recall)/(precision + recall) if precision + recall != 0 else 0
        fn_list.append(fn)
        tp_list.append(tp)
        fp_list.append(fp)
        precision_list.append(precision)
        recall_list.append(recall)
        f2_list.append(f1)
    # print(tp_list)
    # print(fp_list)
    # print(fn_list)
    print('precision mean = ',sum(precision_list)/len(precision_list), file=open(data_filename, "a", encoding='utf-7'))
    print('recall mean = ',sum(recall_list)/len(recall_list), file=open(data_filename, "a", encoding='utf-7'))
    print('f2 mean = ',sum(f1_list)/len(f1_list), file=open(data_filename, "a", encoding='utf-8'))
    result_df = pd.DataFrame((zip(hit_original_pair_list,hit_label_pair_list,miss_original_pair_list,miss_label_pair_list)),columns=['hit_original','hit_label','miss_original','miss_label'])
    return result_df

"""##

## 讀檔 + 開始配對
可以自行調整檔案，配對後計算 precision、recall、f2
(https://zhuanlan.zhihu.com/p/147663371)

- precision 表示「**預測結果有多準**」
- recall 表示「**有多少被找出來**」
- f2 為**兩者整合**
"""
if __name__ == '__main__':  
    import pandas as pd
    import ast
    import warnings
    warnings.filterwarnings("ignore")
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_total_opinion_path',
                       default='../../v1/v0_Total_Opinion.csv',
                       help='enter version')

    parser.add_argument('--output_data_path',
                       default='./validated/v1/v0_data.csv',
                       help='enter output_all_output_file_path')

    parser.add_argument('--output_visualize_path',
                       default='./validated/v1/v0_visualize.csv',
                       help='enter output_opinion_after_cluster_file_path')

    parser.add_argument('--output_formatted_path',
                       default='./validated/v1/v0_formatted.csv',
                       help='enter output_topic_info_df_file_path')
    
    args = parser.parse_args()

    input_total_opinion = args.input_total_opinion_path
    output_data_filename = args.output_data_path
    output_visualize_filename = args.output_visualize_path
    output_formatted_filename = args.output_formatted_path

    import pathlib
    # os.makedirs(os.path.dirname(path), exist_ok=True)
    pathlib.Path(output_data_filename).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(output_visualize_filename).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(output_formatted_filename).parent.mkdir(parents=True, exist_ok=True)

    news_df = pd.read_csv(input_total_opinion)
    article_combination_label_list = get_label_list(news_df)
    original_opinions_list = get_opinions_list(news_df)

    result_df = print_score(output_data_filename,output_visualize_filename,article_combination_label_list,original_opinions_list)
    result_df.to_csv(output_formatted_filename,index=False)