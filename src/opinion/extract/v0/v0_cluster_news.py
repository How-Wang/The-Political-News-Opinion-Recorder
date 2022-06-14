# -*- coding: utf-8 -*-

# V0 使用 BerTopic 分群 2.

from tabnanny import verbose
from matplotlib.pyplot import title
from torch import embedding


def get_news_cluster(title_list):
    topics,_ = fair_ckip_topic_model.fit_transform(title_list)
    representative_docs_dict = fair_ckip_topic_model.get_representative_docs()
    # topics,_ = topic_model.fit_transform(title_list)
    # representative_docs_dict = topic_model.get_representative_docs()
    return topics, representative_docs_dict

def top(file_full_name):
    news_df = pd.read_csv(file_full_name)
    news_df['topic'] = ""
    topics, representative_docs_dict = get_news_cluster(news_df['title'])

    news_df['topic'] = topics
    news_df['representative_docs'] = ""
    news_df['representative_docs'].values[:] = 0
    # print(representative_docs_dict)
    # 原始版本，可以拿多篇代表
    # for topics_index in range(len(representative_docs_dict)):
    #     for representative_article in representative_docs_dict[topics_index]:
    #         news_df.loc[news_df['article'] == representative_article ,'representative_docs'] = 1
    
    # 新版本，只拿第一篇文章代表
    for topics_index in range(len(representative_docs_dict)):
        representative_title = representative_docs_dict[topics_index][0]
        news_df.loc[news_df['title'] == representative_title ,'representative_docs'] = 1

    topic_index = []
    # topic_article_index = []
    topic_represent_article = []
    topic_ner_dic = []
    for i in range(max(topics)+1):
        topic_index.append(i)
        # topic_article_index.append([])
        topic_ner_dic.append({})
    # print(topic_ner_dic)
    # print(max(topics))
    # print(len(topic_ner_dic))

    # for topic ner
    for i in range(len(news_df)):
        if news_df.iloc[i]['topic'] != -1:
            # print(type(news_df.iloc[i]['ner']))
            news_ner_list = ast.literal_eval(news_df.iloc[i]['ner'])
            for ner_name in news_ner_list:
                if ner_name in topic_ner_dic[news_df.iloc[i]['topic']].keys():
                    topic_ner_dic[news_df.iloc[i]['topic']][ner_name] += 1
                else:
                    topic_ner_dic[news_df.iloc[i]['topic']][ner_name] = 0
            # topic_article_index[news_df.iloc[i]['topic']].append(i)
    
    # for topic represent article
    for topic_i in range(max(topics)+1):
        for news_row in range(len(news_df)):
            if news_df.iloc[news_row]['topic'] == topic_i and news_df.iloc[news_row]['representative_docs'] == 1:
                topic_represent_article.append(news_row)
    # print(topic_represent_article)

    topic_info_df = pd.DataFrame(list(zip(topic_index,topic_represent_article,topic_ner_dic)),columns=['topic_index','topic_represent_article','topic_ner_dic'])
    return news_df, topic_info_df

if __name__ == '__main__':
    import pandas as pd
    import ast
    from bertopic import BERTopic
    from flair.embeddings import TransformerDocumentEmbeddings
    import argparse
    import pathlib

    # from google.cloud import bigquery
    # from google.cloud.exceptions import NotFound
    import pandas as pd

    # get the file path from arg
    parser = argparse.ArgumentParser()
    # topic_model = BERTopic(embedding_model="ckiplab/bert-base-chinese")
    bert = TransformerDocumentEmbeddings("ckiplab/bert-base-chinese")
    fair_ckip_topic_model = BERTopic(embedding_model=bert,verbose=True)

    parser.add_argument('--input_news_file_path',
                       default='./result/v0_Total_Opinion.csv',
                       help='enter input news data csv file path')

    parser.add_argument('--output_all_output_file_path',
                       default='./result/v0_Total_Opinion.csv',
                       help='enter output_all_output_file_path')

    parser.add_argument('--output_topic_info_df_file_path',
                    default='./result/v0_topic_info.csv',
                    help='enter output_topic_info_df_file_path')

    args = parser.parse_args()
    file_full_name = args.input_news_file_path # file_full_name = './result/v0_Total_Opinion.csv'
    all_output_file = args.output_all_output_file_path # all_output_file = "./result/v0_Total_Opinion.csv"
    topic_info_file = args.output_topic_info_df_file_path

    news_df, topic_info_df =  top(file_full_name)

    pathlib.Path(all_output_file).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(topic_info_file).parent.mkdir(parents=True, exist_ok=True)

    topic_info_df.to_csv(topic_info_file,index=False)
    news_df.to_csv(all_output_file, index=False)
