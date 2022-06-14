# -*- coding: utf-8 -*-

# V0  代名詞代換  1.

"""## 1.代名詞代換

### function 定義
#### 將一字名稱代換
- 呼叫 change_ner_one_word_name( ) 即可  
- ex: `鄭(麗文)` 痛罵 `蘇(貞昌)`
"""

def get_person_entity_list(ner_list):
  # Get the list contain changed person candidates
  person_entity_list = []
  for ner_item in ner_list:
    if ((ner_item[1] in ["PERSON"]) and (2<=len(ner_item[0])<=4) ) or ((ner_item[1] in ["ORG","NORP"]) and (3 <= len(ner_item[0]))): # 
      already_inside = False
      # run through all person in candidates
      for person_item in person_entity_list:
        # have exist in candidate, count add 1
        if ner_item[0] == person_item[0]:
          already_inside = True
          person_item[1] += 1
      # not exist in candidate, append it
      if already_inside == False:
        person_entity_list.append([ner_item[0],0])
  return person_entity_list

def remove_same_first_name_person(person_entity_list):
  # calculate the show count, in order to change person candidate place having same first name
  for item1 in person_entity_list:
    for item2 in person_entity_list:
      # if item not the same, but have same first name
      # move the less show up one to last
      if item1 != item2 and item1[0][0] == item2[0][0]:
        # move less one to last
        if item1[1] < item2[1]:
          person_entity_list.append(person_entity_list.pop(person_entity_list.index(item1)))
        elif item1[1] > item2[1]:
          person_entity_list.append(person_entity_list.pop(person_entity_list.index(item2)))
        elif len(item1[0]) > len(item2[0]):
          person_entity_list.append(person_entity_list.pop(person_entity_list.index(item1)))
        else:
          person_entity_list.append(person_entity_list.pop(person_entity_list.index(item2)))
  return person_entity_list

def change_ner_one_word_name(input_document):
  input_document = input_document.replace(" ","")
  doc = CkipDocument(raw=input_document)
  # Named-Entity Recognition
  pipeline.get_ner(doc)
  ner_list = doc.ner.to_list()
  # change 2d to 1d array
  ner_list = list(chain.from_iterable(ner_list))
  # temp save original ner for later to return
  original_ner_list = [ner[0] for ner in ner_list.copy() if ner[1] not in ['DATE','CARDINAL','PERCENT','QUANTITY','TIME','ORDINAL']]
  
  # call "person entity function"
  person_entity_list = get_person_entity_list(ner_list)
  # call "remove same first name person" function
  person_entity_list = remove_same_first_name_person(person_entity_list)
  # leave person name
  person_entity_list = list([item[0] for item in person_entity_list])

  # sort the place of ner list
  ner_list.sort(key=lambda x: x[2][0], reverse=False)
  # leave the PERSON ner
  ner_list = [[ner_item[0],ner_item[1],(ner_item[2][0],ner_item[2][1])] for ner_item in ner_list if ner_item[1]=='PERSON']

  # change one word name to person entity name
  for i in range(len(ner_list)):
    if ner_list[i][0] not in person_entity_list and ner_list[i][1]=='PERSON' and len(ner_list[i][0]) < 3:
      for person_entity_item in person_entity_list:
        # first name is same, need change
        if ner_list[i][0][0] == person_entity_item[0]:
          new_word_len = len(person_entity_item)
          old_word_len = len(ner_list[i][0])
          input_document = input_document[:ner_list[i][2][0]] + person_entity_item + input_document[ner_list[i][2][1]:]
          for j in range(i+1,len(ner_list)):
            ner_list[j][2] = (ner_list[j][2][0] + (new_word_len-old_word_len), ner_list[j][2][1] + (new_word_len-old_word_len))
  return person_entity_list,input_document,original_ner_list

"""## 5. 開始實作

### 1.
"""
def top(file_full_name):
    """## 載檔"""
    news_df = pd.read_csv(file_full_name)
    input_document_list = news_df['article'].tolist()
    document_coref_list = []
    people_name_list = []
    article_ner_list = []
    for i in range(len(input_document_list)):
        try:
            article_person_name,document_coref,article_ner = change_ner_one_word_name(input_document_list[i])
            people_name_list.append(article_person_name)
            document_coref_list.append(document_coref)
            article_ner_list.append(article_ner)
        # print(document_coref)
        except:
            people_name_list.append("")
            document_coref_list.append("")
            article_ner_list.append("")

    article_coref_df = pd.Series(document_coref_list)
    news_df['article_coref'] = article_coref_df

    people_name_df = pd.Series(people_name_list)
    news_df['people_name'] = people_name_df

    article_ner_df = pd.Series(article_ner_list)
    news_df['ner'] = article_ner_df

    return news_df


if __name__ == '__main__':
    from ckipnlp.pipeline import CkipPipeline, CkipDocument
    import pandas as pd
    from itertools import chain
    import argparse
    import pathlib
    # from google.cloud import bigquery
    # from google.cloud.exceptions import NotFound
    import pandas as pd

    # declared API 
    pipeline = CkipPipeline(opts={'con_parser': {'username': '', 'password': ''}})
    
    # get the file path from arg
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                      #  default='../../../label/political_news_label_0_to_99.csv',
                       help='enter input news data csv file path')

    parser.add_argument('--output_all_output_file_path',
                      #  default='./result/v1_Total_Opinion.csv',
                       help='enter output_all_output_file_path')
    
    args = parser.parse_args()
    file_full_name = args.input_news_file_path # file_full_name = '../../label/political_news_label_0_to_99.csv'
    all_output_file = args.output_all_output_file_path # all_output_file = "v0_Total_Opinion.csv"

    news_df = top(file_full_name)
    pathlib.Path(all_output_file).parent.mkdir(parents=True, exist_ok=True)
    news_df.to_csv(all_output_file, index=False)

