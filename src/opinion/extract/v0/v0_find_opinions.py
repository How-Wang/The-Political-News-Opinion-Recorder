# -*- coding: utf-8 -*-

# V0 找出結尾與開頭 3.

"""## 3. 利用 rule-based 找出結尾與開頭
- 根據對應到的自定義動詞
- 回頭找被對應到的人名
- 動主詞距離不超過 30 字
- 意見大於 10 字
- 主詞前不可有介係詞

### function 定義
"""

def get_ner_contain_place_list(article,people_name_list):
  # after change one name, 
  # find all name place
  ner_contain_place_list = []
  for name in people_name_list:
    # print(name)
    try:
      for m in re.finditer(name, article):
        # print(m)
        temp_ner_item = (m.start(0), m.end(0), name)
        ner_contain_place_list.append(temp_ner_item)
    except:
      continue
  # sort list
  ner_contain_place_list.sort(key=lambda x:x[0])

  return ner_contain_place_list


def get_rule_based_opinion(article,ner_contain_place_list):
    # print(type(ner_contain_place_list))
    people_opinion_list =[]
    # find the verb and opinion end index by regux
    pattern = "(提到|說明|說|表示|指出|說道|宣布|解釋|強調|有感而發|表示|回應|強調|指出|解釋|批評|評估|提出|呼籲|質疑|認為|不禁問道|發現|痛批)(，|:「|：|:|;|,)*(.+?)(。)(」)*"
    result = [(m.start(3), m.end(0), m.start(1),m.end(1)) for m in re.finditer(pattern, article)]
    # print(result)
    order = 0
    for (begin, end, verb_begin, verb_end) in result:
        # print(begin, end, verb)
        # if begin begin end is too close, next one
        if end - begin < 10:
            continue
        # got spken words
        spoken_words = article[begin:end]
        # got verb words
        verb_words = article[verb_begin:verb_end]
        # find name ner candidate (in front of verb)
        filtered_ner_list = [item for item in ner_contain_place_list if (item[1]<=begin) ]
        # set words i don't want before person name
        not_want_words_list = ['於','在','受']
        # default set the person i want, as close as possible to verb
        words_index = -1
        # start to find opinions person
        while(1):
            if -words_index > len(filtered_ner_list):
                break
            try:
                if any(not_want_words in article[filtered_ner_list[words_index][0]-3:filtered_ner_list[words_index][0]] for not_want_words in not_want_words_list):
                    # if before ner, there is the word i don't want. 
                    # discard and change to other candidate
                    words_index -= 1
                else:
                    # got the person!
                    person_name = filtered_ner_list[words_index][2]
                    if begin - filtered_ner_list[words_index][0] <= 30:
                        # if not too long, accept it
                        people_opinion_list.append([[{'start':filtered_ner_list[words_index][0], 
                                                    'end':filtered_ner_list[words_index][1], 
                                                    'text':person_name,
                                                    'labels': ['person']
                                                    },{
                                                    'start': begin,
                                                    'end': end, 
                                                    'text': spoken_words,
                                                    'labels': ['opinion']
                                                    },{
                                                    'start': verb_begin,
                                                    'end': verb_end, 
                                                    'text': verb_words,
                                                    'labels': ['verb']
                                                    }
                                                    ],order])
                        order += 1
                    break
            except:
                break
            
    return people_opinion_list

def top(file_full_name):

    news_df = pd.read_csv(file_full_name)
    news_df['opinions_list'] = ""

    for i in trange(len(news_df)):
        try:
            people_name_list = ast.literal_eval(news_df.iloc[i]['people_name'])
            ner_contain_place_list = get_ner_contain_place_list(news_df.iloc[i]['article_coref'],  people_name_list) #ast.literal_eval()
            news_df['opinions_list'][i] = get_rule_based_opinion(news_df.iloc[i]['article_coref'], ner_contain_place_list)
        except:
            news_df['opinions_list'][i] = []

    return news_df

if __name__ == '__main__':
    import regex as re
    import pandas as pd
    from tqdm import trange
    import ast
    import argparse
    import pathlib
    # from google.cloud import bigquery
    # from google.cloud.exceptions import NotFound
    import pandas as pd

    # get the file path from arg
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                       default='./result/v0_Total_Opinion.csv',
                       help='enter input news data csv file path')

    parser.add_argument('--output_all_output_file_path',
                       default='./result/v0_Total_Opinion.csv',
                       help='enter output_all_output_file_path')
    
    args = parser.parse_args()
    file_full_name = args.input_news_file_path # file_full_name = './result/v0_Total_Opinion.csv'
    all_output_file = args.output_all_output_file_path # all_output_file = "./result/v0_Total_Opinion.csv"

    pathlib.Path(all_output_file).parent.mkdir(parents=True, exist_ok=True)

    news_df = top(file_full_name)
    news_df.to_csv(all_output_file, index=False)

