# -*- coding: utf-8 -*-

# V1 取得 VE2 Agent 3.

def make_conparse(an_article, pipeline):
    doc = CkipDocument(raw=an_article)
    pipeline.get_conparse(doc)
    return doc.conparse[0]

def find_spice_index(an_article):
    return [i for i, char in enumerate(an_article) if char == ' ']

def make_agent_VE2_label(old_article, pipeline):

  spice_index_list = find_spice_index(old_article)
  conparse = make_conparse(old_article, pipeline)
  # print_tree_pic(old_article)

  article = ""
  start = 0
  end = 0
  # every sentence in article have 4 kinds VE2 and agent pairs
  one_to_one_pair = []
  # iterate the clause
  for ParseClause in conparse:
    sentence = ""
    if ParseClause.clause != '':
      VE2_count = 0
      agent_count = 0
      VE2_agent_clause_label = []
      tree = ParseClause.to_tree()
      # iterate every node in sentence to find VE2 and agent
      for node in tree.all_nodes_itr():
        node_dict = node.to_dict()
        node_data = node_dict['data']

        node_id = node_dict['id']
        role = node_data['role']
        pos = node_data['pos']
        word = node_data['word']
        # change index when switch words
        if word != None:
          sentence += word
          start = end
          end = start + len(word)
        else:
          pass
        # find VE2
        if 'VE2' in pos:
          label = {'start': start, 'end': end, 'text': word, 'labels': ['VE2']}

          VE2_agent_clause_label.append(label.copy())
          VE2_count += 1
        # find agent
        if role != None:
          if 'agent' in role:
            if word == None:
              temp_word = ""
              sub_tree = tree.subtree(node_id)
              sub_node_list = sub_tree.all_nodes()
              sub_node_list.sort(key=lambda x: x.to_dict()['id'])
              for sub_node in sub_node_list:
                sub_node_dict = sub_node.to_dict()
                if sub_node_dict['data']['word'] != None:
                  temp_word += sub_node_dict['data']['word']
              temp_start = end
              temp_end = end + len(temp_word)
            else:
              temp_word = word
              temp_start = start
              temp_end = end
            label = {'start': temp_start, 'end': temp_end, 'text': temp_word, 'labels': ['agent']}
            VE2_agent_clause_label.append(label.copy())
            agent_count += 1

    # change index when switch sentence
    sentence += ParseClause.delim
    # print(ParseClause.delim)
    start = end
    end = start + len(ParseClause.delim)
    article += sentence

    # check this sentence's VE2_agent pair belong to which kind
    if VE2_count == 1 and agent_count == 1:
      one_to_one_pair.append(VE2_agent_clause_label.copy())

  # change index when article have space
  for space_index in spice_index_list:
    article = article[:space_index] + " " + article[space_index:]
    for one_to_one_sentence_object in one_to_one_pair:
      for one_to_one_object in one_to_one_sentence_object:
        if one_to_one_object['start'] >= space_index:
          one_to_one_object['start'] += 1
          one_to_one_object['end'] += 1        
    
  return one_to_one_pair

def top(file_full_name,pipeline):
    news_df = pd.read_csv(file_full_name)
    article_list = news_df['article_coref'].tolist()

    news_df['one_to_one_pair'] = ""
    news_df['one_to_one_pair_count'] = 0

    for i in trange(len(news_df)):
        try:
            news_df['one_to_one_pair'][i] = make_agent_VE2_label(article_list[i], pipeline)
            # print(news_df['one_to_one_pair'][i])
        except:
            print('function return error in' + str(i))
            continue
        try:
            news_df['one_to_one_pair_count'][i] = len(news_df['one_to_one_pair'][i])
        except:
            print('one_to_one_pair_count error in' + str(i))
            continue
    return news_df

if __name__ == '__main__':
    from ckipnlp.pipeline import CkipPipeline, CkipDocument
    import pandas as pd
    from tqdm import trange
    # import ast
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

    news_df = top(file_full_name,pipeline)
    news_df.to_csv(all_output_file, index=False)
    