# -*- coding: utf-8 -*-

# V1 找出結尾與開頭 4.

def get_opinion(article,sentence_list,people_name_list):
  # print(type(people_name_list))
  # if type(people_name_list) == str:
  people_name_list = list(ast.literal_eval(people_name_list))
  sentence_list = ast.literal_eval(sentence_list)
  people_opinion_list = []

  tolerance = 3
  end_list = [m.start() for m in re.finditer('。|；|;', article)]
  end_list.append(0)
  end_list.append(len(article))
  end_list.sort()

  not_agent_list = ["你","妳","我","他","她"]
  # sentence agent not he or she, and verb is not in front of agent
  sentence_list = [sentence for sentence in sentence_list if (sentence[1]['text'] not in not_agent_list)]

  order = 0
  for sentence in sentence_list:
    for i in range(len(end_list)-1):

      if end_list[i] - tolerance < sentence[1]['start'] and sentence[0]['end'] <= end_list[i+1]:
        # to find "," place
        start_point = sentence[0]['end']
        start_icon_list = [',']
        for temp_start in range(3):
          if article[start_point+temp_start] in start_icon_list:
            start_point = start_point + temp_start + 1
            break
        
        # to find "」" place
        end_point = end_list[i+1]
        end_icon_list = ["」"]
        for temp_end in range(3):
          if article[start_point + temp_end] in end_icon_list:
            start_point = start_point + temp_end + 1
            break
        if end_point - start_point < 10:
          continue
        opinion = article[start_point:end_point]

        # change the name by candidate name list
        people_name = sentence[1]['text']
        for people_name_candidate in people_name_list:
          if people_name_candidate in sentence[1]['text']:
            people_name = people_name_candidate
            break
        # check agent is in people name_list
        if people_name not in people_name_list:
          continue

        # people_opinion_object = {"person":people_name,"verb":sentence[1]['text'],"opinion":opinion,"order":order}
        people_opinion_object = [[{'start': sentence[1]['start'], 
                                  'end': sentence[1]['end'], 
                                  'text':people_name,
                                  'labels': ['person']
                                  },{
                                  'start':start_point,
                                  'end': end_point, 
                                  'text': opinion,
                                  'labels': ['opinion']
                                  },{
                                  'start': sentence[0]['start'],
                                  'end': sentence[0]['end'], 
                                  'text': sentence[0]['text'],
                                  'labels': ['verb']
                                  }
                                 ]
                                ,order
                                ]
        people_opinion_list.append(people_opinion_object)
        order = order + 1
        
  return people_opinion_list


def top(file_full_name):
  news_df = pd.read_csv(file_full_name)

  news_df['opinions_list'] = ""

  for i in trange(len(news_df)):
      try:
          news_df['opinions_list'][i] = get_opinion(news_df.iloc[i]['article_coref'],news_df.iloc[i]['one_to_one_pair'],news_df.iloc[i]['people_name'])
          # print(news_df['opinions_no_he_and_she'][i])
      except:
          print('error in ',i)
          news_df['opinions_list'][i] = []

  return news_df

if __name__ == '__main__':
    from ckipnlp.pipeline import CkipPipeline
    import regex as re
    import pandas as pd
    from tqdm import trange
    import ast
    import argparse
    import pathlib

    pipeline = CkipPipeline(opts={'con_parser': {'username': '', 'password': ''}})

    # get the file path from arg
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                      #  default='./result/v1_Total_Opinion.csv',
                       help='enter input news data csv file path')

    parser.add_argument('--output_all_output_file_path',
                      #  default='./result/v1_Total_Opinion.csv',
                       help='enter output_all_output_file_path')
    
    args = parser.parse_args()

    file_full_name = args.input_news_file_path # file_full_name = "./v1_Total_Opinion.csv"
    all_output_file = args.output_all_output_file_path # all_output_file = "./v1_Total_Opinion.csv"
    pathlib.Path(all_output_file).parent.mkdir(parents=True, exist_ok=True)

    news_df = top(file_full_name)
    news_df.to_csv(all_output_file, index=False)
    