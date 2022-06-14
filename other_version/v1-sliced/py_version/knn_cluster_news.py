# -*- coding: utf-8 -*-

# V0 KNN新聞分群 2.

"""## 2. 新聞分群"""

def cluster_article(article_list):
    corpus_embeddings = embedder.encode(article_list)  
    # Find out the best score
    sil_coeff_list = []
    least_cluster_num = int(len(corpus_embeddings)/25)
    max_cluster_num = int(len(corpus_embeddings)/10)

    for n_cluster in trange(least_cluster_num,max_cluster_num):
        clustering_model = KMeans(n_clusters=n_cluster).fit(corpus_embeddings)
        label = clustering_model.labels_
        sil_coeff = silhouette_score(corpus_embeddings, label, metric='euclidean')
        sil_coeff_list.append(sil_coeff)

    # Get best clusters
    num_clusters = sil_coeff_list.index(max(sil_coeff_list)) + least_cluster_num
    plt.plot(range(least_cluster_num,max_cluster_num), sil_coeff_list)

    # Perform k-means clustering
    clustering_model = KMeans(n_clusters=num_clusters)
    clustering_model.fit(corpus_embeddings)
    cluster_label_list = clustering_model.labels_

    # Find the closet sentence in every cluster to represent group meaning
    closest_index_list, _ = pairwise_distances_argmin_min(clustering_model.cluster_centers_, corpus_embeddings)
    
    return cluster_label_list, closest_index_list

def top(file_full_name):

    news_df = pd.read_csv(file_full_name)
    topics, representative_docs_dict = cluster_article(news_df['article'])
    news_df['topic'] = topics
    news_df['representative_docs'] = ""
    news_df['representative_docs'].values[:] = 0

    for topics_index in representative_docs_dict:
        news_df['representative_docs'].iloc[topics_index] = 1

    topic_index = []
    topic_article_index = []
    topic_ner_dic = []

    for i in range(max(topics)+1):
        topic_index.append(i)
        topic_article_index.append([])
        topic_ner_dic.append({})

    for i in range(len(news_df)):
        news_ner_list = ast.literal_eval(news_df.iloc[i]['ner'])
        for ner_name in news_ner_list:
            if ner_name in topic_ner_dic[news_df.iloc[i]['topic']].keys():
                topic_ner_dic[news_df.iloc[i]['topic']][ner_name] += 1
            else:
                topic_ner_dic[news_df.iloc[i]['topic']][ner_name] = 0
        topic_article_index[news_df.iloc[i]['topic']].append(i)

    topic_info_df = pd.DataFrame(list(zip(topic_index,representative_docs_dict,topic_ner_dic)),columns=['topic_index','topic_represent_article','topic_ner_dic'])

    return news_df,topic_info_df


if __name__ == '__main__':
    import pandas as pd
    import ast
    from tqdm import trange
    # from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer, util
    from sklearn.cluster import KMeans
    from sklearn.metrics import pairwise_distances_argmin_min, silhouette_score
    import matplotlib.pyplot as plt
    # from google.cloud import bigquery
    # from google.cloud.exceptions import NotFound
    import pandas as pd
    import argparse
    import pathlib

    """#### 輸入 ckip 帳號密碼"""
    embedder = SentenceTransformer('ckiplab/bert-base-chinese')

    # get the file path from arg
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                    #    default='./result/v1_Total_Opinion.csv',
                       help='enter input news data csv file path')

    parser.add_argument('--output_all_output_file_path',
                    #    default='./result/v1_Total_Opinion.csv',
                       help='enter output_all_output_file_path')

    parser.add_argument('--output_topic_info_df_file_path',
                    #   default='./result/v1_topic_info.csv',
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