def download_cluster_pic(date, topic, title):
    import pathlib
    from pathlib import Path
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    import urllib

    FILE_PATH = "../crawler/result/fit_UI/cluster_pic/" + date + "/" + str(topic) + ".png"
    if Path(FILE_PATH).is_file():
        return
    pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)

    # Open up web driver and goes to Google Images
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("start-maximized")
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get('https://www.google.ca/imghp?hl=en&tab=ri&authuser=0&ogbl')
    box = driver.find_element_by_xpath('//*[@id="sbtc"]/div/div[2]/input')
    box.send_keys(title)
    box.send_keys(Keys.ENTER)
    img = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    src = img.get_attribute('src')

    # download the image
    pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(src, FILE_PATH)
    return FILE_PATH

def run_extraction(end_datetime, start_datetime): # 
    import sys
    import datetime
    from datetime import datetime, timedelta
    sys.path.insert(0, '..')

    # today =  datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # end_datetime = today - timedelta(days=0)
    # start_datetime = today - timedelta(days=1)

    end_datetime_str = end_datetime.strftime("%Y-%m-%d")
    start_datetime_str = start_datetime.strftime("%Y-%m-%d")
    print(end_datetime_str, start_datetime, start_datetime_str)

    csv_name = '../crawler/result/processed/'+ start_datetime_str + '_news/' + start_datetime_str +'-news.csv'

    TOPIC_INFO_PATH = '../opinion/extract/result/topic_info.csv' 
    TOTAL_OPINION_PATH = '../opinion/extract/result/total_opinions.csv' 
    PERSON_UNIT_PATH = '../opinion/extract/result/person_unit_opinion.json'
    CCDF_PATH = '../opinion/extract/result/cluster_cluster_table.csv'

    POSI_DICT_PATH = '../opinion/extract/result/sentiment_dict/NTUSD_positive_unicode.txt'
    NEGA_DICT_PATH = '../opinion/extract/result/sentiment_dict/NTUSD_negative_unicode.txt'
    import os

    
    python_return = os.system(f'python  ../crawler/main.py --input_end_date {end_datetime_str} --input_start_date {start_datetime_str}')

    if python_return != 0:
        print('error in crawler')
    else:
        print('='*100, 'crawler pass')
    
    python_return = os.system(f'python  ../pre-processing/main.py --input_start_date {start_datetime_str}')
    if python_return != 0:
        print('error in pre-processing')
    else:
        print('='*100, 'pre-processing pass')

    python_return = os.system(f'python  ../crawler/result/concate.py --input_start_date {start_datetime_str}')
    if python_return != 0:
        print('error in concate a new csv')
    else:
        print('='*100, 'concate pass')

    python_return = os.system(f'python  ../opinion/extract/v0/v0_change_pronoun.py --input_news_file_path {csv_name} --output_all_output_file_path {TOTAL_OPINION_PATH}')
    if python_return != 0:
        print('error in change pronoun')
    else:
        print('='*100, 'change pronoun pass')

    python_return = os.system(f'python  ../opinion/extract/v0/v0_cluster_news.py --input_news_file_path {TOTAL_OPINION_PATH} --output_all_output_file_path {TOTAL_OPINION_PATH} --output_topic_info_df_file_path {TOPIC_INFO_PATH}')
    if python_return != 0:
        print('error in cluster news')
    else:
        print('='*100, 'cluster news pass')

    python_return = os.system(f'python  ../opinion/extract/v0/v0_find_opinions.py --input_news_file_path {TOTAL_OPINION_PATH} --output_all_output_file_path {TOTAL_OPINION_PATH}')
    if python_return != 0:
        print('error in find opinions')
    else:
        print('='*100, 'find opinions pass')

    python_return = os.system(f'python  ../opinion/extract/v0/v0_cluster_opinions.py --input_news_file_path {TOTAL_OPINION_PATH} --output_all_output_file_path {TOTAL_OPINION_PATH} ')
    if python_return != 0:
        print('error in cluster opinions')
    else:
        print('='*100, 'cluster opinions pass')

    python_return = os.system(f'python  ../opinion/extract/v0/v0_sentiment_analyze.py --input_news_file_path {TOTAL_OPINION_PATH} --input_negative_path {NEGA_DICT_PATH} --input_positive_path {POSI_DICT_PATH}')
    if python_return != 0:
        print('error in sentiment analyze')
    else:
        print('='*100, 'sentiment analyze pass')

    python_return = os.system(f'python  ../opinion/extract/v0/v0_person_unit_opinions.py --input_person_unit_path {PERSON_UNIT_PATH} --input_news_file_path {TOTAL_OPINION_PATH} --input_topic_name {TOPIC_INFO_PATH} --input_ccdf {CCDF_PATH}')
    if python_return != 0:
        print('error in person unit opinions')
    else:
        print('='*100, 'person unit opinions pass')
    
    print('='*100, 'end extraction')
    return 0

def fit_UI_format():
    import pandas as pd
    import json
    import datetime
    import heapq
    import ast
    import pathlib
    import shutil
    # CLUSTER_OPINION_PATH = '../opinion/extract/result/cluster_opinion.csv' 
    TOPIC_INFO_PATH = '../opinion/extract/result/topic_info.csv' 
    TOTAL_OPINION_PATH = '../opinion/extract/result/total_opinions.csv'
    CCPATH = '../opinion/extract/result/cluster_cluster_table.csv'
    PERSON_UNIT_OPINION_PATH = '../opinion/extract/result/person_unit_opinion.json'
    FIT_UI_PATH = '../crawler/result/fit_UI/'
    total_df = pd.read_csv(TOTAL_OPINION_PATH)
    TIME_PREFIX = datetime.datetime.strptime(total_df.iloc[1]['datetime'], '%Y-%m-%d %H:%M').strftime("%Y-%m-%d")

    # opinions_df = pd.read_csv(CLUSTER_OPINION_PATH)
    topic_info_df = pd.read_csv(TOPIC_INFO_PATH)
    print(type(total_df.iloc[1]['datetime']), total_df.iloc[1]['datetime'])

    # Topic page=====================================================================
    topic_list = []
    for i in range(len(topic_info_df)):
        num = topic_info_df.iloc[i]['topic_represent_article']
        topic_item = [i,total_df.iloc[num]['title'], total_df.iloc[num]['article'],TIME_PREFIX]
        topic_list.append(topic_item)
    topic_dict = {"topic_list":topic_list}

    TABLE_NAME_PATH = FIT_UI_PATH + TIME_PREFIX + "-page-dataset" + "/page-table" + ".json"
    pathlib.Path(TABLE_NAME_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(TABLE_NAME_PATH, 'w', encoding='utf-8') as f:
        json.dump(topic_dict, f, ensure_ascii=False, indent=4)

    # Cluster list=====================================================================
    topic_num = len(topic_info_df)
    today_json_list = []
    for i in range(topic_num):
        today_json_list.append({"date":TIME_PREFIX, "topic":i, "article_list":[]})
    for i in range(len(total_df)):
        article = total_df.iloc[i]["article"]
        title = total_df.iloc[i]["title"]
        topic = total_df.iloc[i]["topic"]
        if topic == -1:
            continue
        if total_df.iloc[i]["representative_docs"] == 1:
            today_json_list[topic]["represent_article"] = article
            today_json_list[topic]["represent_title"] = title
            today_json_list[topic]["represent_news_id"] = i
            # download picture for cluster
            download_cluster_pic(TIME_PREFIX, topic, title)
        else:
            today_json_list[topic]["article_list"].append([title,article,i])
    for i in range(topic_num):
        tag_dict = ast.literal_eval(topic_info_df.iloc[i]["topic_ner_dic"])
        today_json_list[i]["tag"] = heapq.nlargest(5, tag_dict, key=tag_dict.get)

    for i in range(len(today_json_list)):
        TABLE_NAME_PATH = FIT_UI_PATH + TIME_PREFIX + "-cluster-list-dataset/" + "cluster-" + str(today_json_list[i]["topic"]) + "-table.json"
        pathlib.Path(TABLE_NAME_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(TABLE_NAME_PATH, 'w', encoding='utf-8') as f:
            json.dump(today_json_list[i], f, ensure_ascii=False, indent=4)

    # Opinions =====================================================================
    all_news_json_list = []
    for i in range(len(total_df)):
        article = total_df.iloc[i]["article"]
        title = total_df.iloc[i]["title"]
        opinions = total_df.iloc[i]["all_opinions_after_cluster"]
        little_topic = total_df.iloc[i]['topic']
        all_news_json_list.append({"date":TIME_PREFIX,"news_id":i,"title":title,"article":article,"opinions":opinions,"little_topic": str(little_topic)}) 

    # save every news opinion
    for i in range(len(all_news_json_list)):
        TABLE_NAME_PATH = FIT_UI_PATH + TIME_PREFIX + "-opinions-dataset/" + str(i) + "-table.json"
        pathlib.Path(TABLE_NAME_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(TABLE_NAME_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_news_json_list[i], f, ensure_ascii=False, indent=4)

    # Personal Opinions =====================================================================
    # create a new sliced fit UI result
    # compare person_unit_opinion_dict(little cluster but not change) and ccdf(total cluster but change every day)
    with open(PERSON_UNIT_OPINION_PATH,encoding="utf-8") as json_file:
        person_unit_opinion_dict = json.load(json_file)
    
    # read cluster_cluster dataframe
    cluster_cluster_df = pd.read_csv(CCPATH)

    # delete older one, and refresh it
    SLICED_DIR_PATH = FIT_UI_PATH + 'person-sliced-dataset/'
    if pathlib.Path(SLICED_DIR_PATH).is_dir():
        shutil.rmtree(SLICED_DIR_PATH)

    # start to add one by one
    for name in person_unit_opinion_dict:
        # append all small_cluster to total_cluster.json
        for small_cluster in person_unit_opinion_dict[name]['opinions']:
            # find total_cluster which is belonged to small_cluster
            for cc_index in range(len(cluster_cluster_df)):
                if cluster_cluster_df.iloc[cc_index]['little_cluster_title'] == small_cluster:
                    total_cluster_number = cluster_cluster_df.iloc[cc_index]['total_cluster_number']
            # look this total_cluster.json need to create or not
            TEMP_SLICED_PATH = SLICED_DIR_PATH + name + '-' + str(total_cluster_number) + '.json'
            try:
                with open(TEMP_SLICED_PATH, encoding="utf-8") as json_file:
                    pubc_dict = json.load(json_file)
            except:
                pubc_dict = {'pict_path':person_unit_opinion_dict[name]['pic_path'], 'opinions':[]}
            # append all news from one small cluster to total cluster
            for opinions in person_unit_opinion_dict[name]['opinions'][small_cluster]:
                pubc_dict['opinions'].append(opinions)
            # save total_cluster.json file
            pathlib.Path(TEMP_SLICED_PATH).parent.mkdir(parents=True, exist_ok=True)
            with open(TEMP_SLICED_PATH, 'w', encoding='utf-8') as fp:
                json.dump(pubc_dict, fp,  indent=4, ensure_ascii=False)

    print('='*100, 'end fit UI')
    return
