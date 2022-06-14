# -*- coding: utf-8 -*-

# V0 使用 K-means 分群、cosine-similarity 判斷相似性 4.

"""## 4. 使用 K-means 並串接 Dataset
1. 使用 sentenceTransformer 套件作為 embedder
2. 找出最適合的分群群數
3. 找出每一群中，最接近中心點的句子作為代表
4. 根據 model clustered label list 分配每個句子到所屬的 clustered list 
5. 印出最終結果
"""

def cluster_article_opinions(combine_opinions_dict):
    opinions_after_cluster  = []
    for name_key in combine_opinions_dict.keys():
        order_list = [item[2] for item in combine_opinions_dict[name_key]]
        verb_list = [item[0] for item in combine_opinions_dict[name_key]]
        corpus = [item[1] for item in combine_opinions_dict[name_key]]
        corpus_embeddings = embedder.encode(corpus)

        if len(corpus)== 1:
            opinions_after_cluster.append({"person":name_key,"verb":verb_list[0],"opinion":corpus[0],"order":order_list[0]})
            continue
        elif len(corpus)== 2:
            # compare the cosine similarity if bigger than 0.8, choose shorter one
            cosine_scores = util.cos_sim(corpus_embeddings[0], corpus_embeddings[1])
            if cosine_scores > 0.8:
                if(len(corpus_embeddings[0]) < len(corpus_embeddings[1])):
                    opinions_after_cluster.append({"person":name_key,"verb":verb_list[0],"opinion":corpus[0],"order":order_list[0]})
                else:
                    opinions_after_cluster.append({"person":name_key,"verb":verb_list[1],"opinion":corpus[1],"order":order_list[1]})
            continue
        
        # Find out the best score
        sil_coeff_list = []
        least_cluster_num = 2
        if  5 >= len(corpus) > 3:
            least_cluster_num = len(corpus) - 2
        elif  7 >= len(corpus_embeddings) > 5:
            least_cluster_num = len(corpus_embeddings) - 3
        elif len(corpus_embeddings) > 7:
            least_cluster_num = len(corpus_embeddings) - 4

        for n_cluster in range(least_cluster_num, len(corpus_embeddings)):
            clustering_model = KMeans(n_clusters=n_cluster).fit(corpus_embeddings)
            label = clustering_model.labels_
            sil_coeff = silhouette_score(corpus_embeddings, label, metric='euclidean')
            sil_coeff_list.append(sil_coeff)


        num_clusters = sil_coeff_list.index(max(sil_coeff_list)) + least_cluster_num
        plt.plot(range(least_cluster_num,len(corpus_embeddings)), sil_coeff_list)

        # Perform k-means clustering
        clustering_model = KMeans(n_clusters=num_clusters)
        clustering_model.fit(corpus_embeddings)
        cluster_label_list = clustering_model.labels_

        # Find the closet sentence in every cluster to represent group meaning
        closest_index_list, _ = pairwise_distances_argmin_min(clustering_model.cluster_centers_, corpus_embeddings)

        # Group all sentences into their clustered_sentences_list
        clustered_sentences_list = [[] for i in range(num_clusters)]
        for sentence_id, cluster_id in enumerate(cluster_label_list):
            clustered_sentences_list[cluster_id].append(corpus[sentence_id])

        for i, clustered_sentences in enumerate(clustered_sentences_list):
            opinions_after_cluster.append({"person":name_key, "verb":verb_list[closest_index_list[i]], "opinion":corpus[closest_index_list[i]], "order":order_list[closest_index_list[i]]})
    
    return opinions_after_cluster

def remove_duplicate_same_article_sentence(article_opinions):
    sentences = [opinion_object['opinion'] for opinion_object in article_opinions]
    paraphrases = util.paraphrase_mining(embedder, sentences)
    for paraphrase in paraphrases:
        score, i, j = paraphrase
        if score > 0.95:
            if len(sentences[i]) <= len(sentences[j]):
                article_opinions[i] = ""
            else:
                article_opinions[j] = ""
    article_opinions = [x for x in article_opinions if x]

    return article_opinions

"""## 開始實作

### 4.
"""
def top(file_full_name):
    news_df = pd.read_csv(file_full_name)
    all_opinions_after_cluster = []
    for i in range(len(news_df)):
        opinions_list = ast.literal_eval(news_df.iloc[i]["opinions_list"])
        combine_opinions_dict = {}
        for opinions in opinions_list:
            order = opinions[1]
            for opinion_item_dict in opinions[0]:
                if opinion_item_dict['labels'][0] == 'person':
                    person_name = opinion_item_dict['text']
                elif opinion_item_dict['labels'][0] == 'verb':
                    verb_words = opinion_item_dict['text']
                elif opinion_item_dict['labels'][0] == 'opinion':
                    opinion_words = opinion_item_dict['text']
            # the opinions in reasonable count
            if 10 < len(opinion_words) < 150: #  and opinions['person'] in name_list
                if person_name in combine_opinions_dict.keys():
                    combine_opinions_dict[person_name].append([verb_words,opinion_words,order])
                else:
                    combine_opinions_dict[person_name] = []
                    combine_opinions_dict[person_name].append([verb_words,opinion_words,order])
        opinions_after_cluster = cluster_article_opinions(combine_opinions_dict)
        all_opinions_after_cluster.append(opinions_after_cluster)

    for i in range(len(all_opinions_after_cluster)):
        try:
            all_opinions_after_cluster[i] = remove_duplicate_same_article_sentence(all_opinions_after_cluster[i])
        except:
            pass

    s = pd.Series(all_opinions_after_cluster,name='all_opinions_after_cluster')
    # new_cluster_opinions_df = pd.concat([news_df['title'],news_df['article'], s], axis=1)
    news_df['all_opinions_after_cluster'] = s

    return news_df#, new_cluster_opinions_df 

if __name__ == '__main__':
    import pandas as pd
    from tqdm import trange
    import ast
    from sentence_transformers import SentenceTransformer, util
    from sklearn.cluster import KMeans
    from sklearn.metrics import pairwise_distances_argmin_min, silhouette_score
    import matplotlib.pyplot as plt
    import argparse
    import pathlib
    # from google.cloud import bigquery
    # from google.cloud.exceptions import NotFound
    import pandas as pd

    """#### 輸入 ckip 帳號密碼"""
    embedder = SentenceTransformer('ckiplab/bert-base-chinese')

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                       default='./result/v0_Total_Opinion.csv',
                       help='enter input news data csv file path')

    parser.add_argument('--output_all_output_file_path',
                       default='./result/v0_Total_Opinion.csv',
                       help='enter output_all_output_file_path')

    # parser.add_argument('--output_opinion_after_cluster_file_path',
    #                    default='./result/v0_cluster_opinions.csv',
    #                    help='enter output_opinion_after_cluster_file_path')

    """## 載檔"""

    args = parser.parse_args()
    file_full_name = args.input_news_file_path

    # call top function
    # news_df,new_cluster_opinions_df = top(file_full_name)
    news_df = top(file_full_name)

    # change the dataframe to csv
    all_output_file = args.output_all_output_file_path
    # opinion_after_cluster_file = args.output_opinion_after_cluster_file_path

    # create parents directories
    pathlib.Path(all_output_file).parent.mkdir(parents=True, exist_ok=True)
    # pathlib.Path(opinion_after_cluster_file).parent.mkdir(parents=True, exist_ok=True)

    # save dataframe from function return
    news_df.to_csv(all_output_file, index=False)
    # new_cluster_opinions_df.to_csv(opinion_after_cluster_file,index=False)
