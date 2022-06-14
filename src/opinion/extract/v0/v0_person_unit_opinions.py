def download_pic(people_name):
    FILE_PATH = "../crawler/result/fit_UI/pic/" + people_name + ".png"
    if Path(FILE_PATH).is_file():
        return
    # Open up web driver and goes to Google Images
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("start-maximized")
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get('https://www.google.ca/imghp?hl=en&tab=ri&authuser=0&ogbl')
    box = driver.find_element_by_xpath('//*[@id="sbtc"]/div/div[2]/input')
    box.send_keys(people_name)
    box.send_keys(Keys.ENTER)
    img = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    src = img.get_attribute('src')

    # download the image
    FILE_PATH = "../crawler/result/fit_UI/pic/" + people_name + ".png"
    pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(src, FILE_PATH)
    return FILE_PATH

def find_name_and_pic(name,person_unit_opinion_dict):
    for candidate in person_unit_opinion_dict.keys():
        # print(candidate)
        if name in candidate or candidate in name:
            return candidate, person_unit_opinion_dict[candidate]['pic_path']
    person_unit_opinion_dict[name] = {}
    person_unit_opinion_dict[name]['pic_path'] = download_pic(name)
    person_unit_opinion_dict[name]['opinions'] = {}
    return name, person_unit_opinion_dict[name]['pic_path']

def cluster_article(article_list):
    import numpy as np
    if len(article_list) == 2:
        return np.array([0,1]), np.array([0,1])
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import KMeans
    from sklearn.metrics import pairwise_distances_argmin_min, silhouette_score
    embedder = SentenceTransformer('ckiplab/bert-base-chinese')
    corpus_embeddings = embedder.encode(article_list)  
    # Find out the best score
    sil_coeff_list = []
    least_cluster_num = 2
    max_cluster_num = 2 if int(len(corpus_embeddings)/10) <= 2 else int(len(corpus_embeddings)/10)
    if least_cluster_num == max_cluster_num:
        max_cluster_num += 1
    for n_cluster in range(least_cluster_num,max_cluster_num):
        clustering_model = KMeans(n_clusters=n_cluster).fit(corpus_embeddings)
        label = clustering_model.labels_
        sil_coeff = silhouette_score(corpus_embeddings, label, metric='euclidean')
        sil_coeff_list.append(sil_coeff)

    # Get best clusters
    num_clusters = sil_coeff_list.index(max(sil_coeff_list)) + least_cluster_num

    # Perform k-means clustering
    clustering_model = KMeans(n_clusters=num_clusters)
    clustering_model.fit(corpus_embeddings)
    cluster_label_list = clustering_model.labels_

    # Find the closet sentence in every cluster to represent group meaning
    closest_index_list, _ = pairwise_distances_argmin_min(clustering_model.cluster_centers_, corpus_embeddings)
    
    return cluster_label_list, closest_index_list

def top(person_unit_full_name, file_full_name, topic_full_name, CCPATH):
    # read total file and person unit file
    news_df = pd.read_csv(file_full_name)
    topic_df = pd.read_csv(topic_full_name)

    TIME_PREFIX = datetime.datetime.strptime(news_df.iloc[1]['datetime'], '%Y-%m-%d %H:%M').strftime("%Y-%m-%d")

    # read person unit opinion (little cluster)
    try:
        with open(person_unit_full_name,encoding="utf-8") as json_file:
            person_unit_opinion_dict = json.load(json_file)
    except:
        print("create empty person unit opinion")
        person_unit_opinion_dict = {}

    # read cluster_cluster dataframe (total cluster)
    try:
        cluster_cluster_df = pd.read_csv(CCPATH)
    except:
        print("create empty cluster_cluster_df ")
        cluster_cluster_df = pd.DataFrame(columns = ['little_cluster_title', 'little_cluster_number', 'date', 'total_cluster_title', 'total_cluster_number'])

    # append new little cluster to ccdf form news_df and topic
    for i in range(len(topic_df)):
        little_cluster = topic_df.iloc[i]['topic_index']
        represent_title = news_df.iloc[topic_df.iloc[i]['topic_represent_article']]['title']
        temp_df = pd.DataFrame({'little_cluster_title':represent_title, 'little_cluster_number':little_cluster, 'date':TIME_PREFIX, 'total_cluster_title':np.nan, 'total_cluster_number':np.nan}, index=[0])
        cluster_cluster_df = cluster_cluster_df.append(temp_df, ignore_index=True)

    # implement knn for ccdf total cluster
    topic_index_list, represent_index_list = cluster_article(cluster_cluster_df['little_cluster_title'])

    # add total cluster info to ccdf
    total_cluster_title_list = []
    for i in range(len(topic_index_list)):
        temp_represent_index =  represent_index_list[topic_index_list[i]]
        total_cluster_title_list.append(cluster_cluster_df.iloc[temp_represent_index]['little_cluster_title'])
    cluster_cluster_df['total_cluster_title'] = total_cluster_title_list
    cluster_cluster_df['total_cluster_number'] = topic_index_list

    # create pic image link
    for i in range(len(news_df)):
        opinions_list = ast.literal_eval(news_df.iloc[i]["opinions_list"])
        for opinions in opinions_list:
            for opinions_item in opinions[0]:
                label = opinions_item['labels']
                text = opinions_item['text']
                if label == ['person']:
                    find_name_and_pic(text, person_unit_opinion_dict)

    # change all_opinions name
    for i in range(len(news_df)):
        opinions_list = ast.literal_eval(news_df.iloc[i]["all_opinions_after_cluster"])
        for j in range(len(opinions_list)):
            # find person row
            # add opinions including time stamp
            opinions_list[j]['person'],_ = find_name_and_pic(opinions_list[j]['person'],person_unit_opinion_dict)
        news_df.iloc[i, news_df.columns.get_loc('all_opinions_after_cluster')] = str(opinions_list)

    # add total_cluster represent title and represent index in news_df
    represent_index_list = []
    represent_title_list = []
    for i in range(len(news_df)):
        topic_index = news_df.iloc[i]['topic']
        temp_represent_index = topic_df.iloc[topic_index]['topic_represent_article']
        represent_index_list.append(temp_represent_index)
        represent_title_list.append(news_df.iloc[temp_represent_index]['title'])
    news_df['represent_index'] = represent_index_list
    news_df['represent_title'] = represent_title_list

    # add person new opinions form little cluster (since it will never change)
    for i in range(len(news_df)):
        represent_title = news_df.iloc[i]['represent_title']
        opinions_list = ast.literal_eval(news_df.iloc[i]["all_opinions_after_cluster"])
        for opinion in opinions_list:
            opinion['datetime'] = news_df.iloc[i]['datetime']
            del opinion['order']
            # find person row
            # add opinions including time stamp
            name,_ = find_name_and_pic(opinion['person'],person_unit_opinion_dict)
            opinion['person'] = name

            if represent_title not in person_unit_opinion_dict[name]['opinions']:
                person_unit_opinion_dict[name]['opinions'][represent_title] = []

            person_unit_opinion_dict[name]['opinions'][represent_title].append(opinion)

    return person_unit_opinion_dict, news_df, topic_df, cluster_cluster_df

if __name__ == '__main__':
    # Imports Packages
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    import urllib
    import pandas as pd
    import numpy as np
    import json
    import pathlib
    from pathlib import Path
    import ast
    import argparse
    import datetime

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_news_file_path',
                    default='../opinion/extract/result/total_opinions.csv',
                    help='enter input news data csv file path')
    parser.add_argument('--input_topic_name',
                       default='../opinion/extract/result/topic_info.csv',
                       help='enter input_topic_name')
    parser.add_argument('--input_person_unit_path',
                       default='../opinion/extract/result/person_unit_opinion.json',
                       help='enter input person unit opinions file path')
    parser.add_argument('--input_ccdf',
                       default='../opinion/extract/result/cluster_cluster_table.csv',
                       help='enter ccdf')

    args = parser.parse_args()
    file_full_name = args.input_news_file_path
    topic_full_name = args.input_topic_name
    person_unit_full_name = args.input_person_unit_path
    cluster_cluster_name = args.input_ccdf

    # call the top function
    person_unit_opinion_dict, news_df, topic_df, cluster_cluster_df= top(person_unit_full_name, file_full_name,topic_full_name,cluster_cluster_name)

    # save person_unit_opinion.json and all info
    with open(person_unit_full_name, 'w', encoding='utf-8') as fp:
        json.dump(person_unit_opinion_dict, fp,  indent=4, ensure_ascii=False)
    cluster_cluster_df.to_csv(cluster_cluster_name, index=False)
    topic_df.to_csv(topic_full_name, index=False)
    news_df.to_csv(file_full_name, index=False)

