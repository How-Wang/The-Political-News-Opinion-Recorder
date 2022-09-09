# 檔案架構
- src
    - crawler
        - result
            - fit_UI
                >==`所有網頁上需要呈現的資料`==
                - person-slice-dataset
                    >==`以人物＋跨天議題（big cluster）為單位切分`==
                    - 馬英九0.json
                    - 馬英九1.json
                    - 蔡英文0.json
                    - ......
                - pic
                    - 馬英九.png
                    - 蔡英文.png
                    - ......
                - cluster_pic
                    - ......
                - 2022-05-21-cluster-list-dataset
                    - cluster-0-table.json
                    - cluster-1-table.json
                    - ......
                - 2022-05-21-opinions-dataset
                    - 0-table.json
                    - 1-table.json
                    - ......
                - 2022-05-21-page-dataset
                    - page-table.json
                - 2022-05-22-cluster-list-dataset
                - ......
            - processed
                >==`前處理完的爬蟲資料`==
                - 2022-05-21_news
                    - **2022-05-21-news.csv** -> 已經被`concate.py`串在一起
                    - 2022-05-21_chinatimes.csv
                    - 2022-05-21_cna.csv
                    - ......
                - 2022-05-22_news
                - ......
            - raw
                >==`第一筆爬蟲資料`==
                - 2022-05-21_news
                    - 2022-05-21_chinatimes.csv
                    - 2022-05-21_cna.csv
                    - ......
                - 2022-05-22_news
                - ......
            - concate.py
                >==`將前處理完的多家新聞資料串在一起`==
        - `many crawler .py code`
            >改路徑要從本身的crawler .py處理，不是 main.py
        - main.py
            >==`爬蟲 code 整理中心`== 會被 `opinion/extract/v0/v0_run.py/run_extraction()`呼叫 
    - opinion
        - extract
            - result
                - person_unit_opinion.json
                    >==`存放全部person人物資訊`==，也會在 v0_person_unit_opinions.py 被切分，再被放到 `crawler/result/fit_UI/person-slice-dataset`
                - topic_info.csv
                    >==`暫時存放當日的新聞分群資訊`==
                - total_opinions.csv
                    >==`暫時存放當日的新聞資訊`==
                - cluster_cluster_table.scv
                    >==`每日新聞分群（small cluster）vs 每日分群後標題的再次分群（big cluster 就是為了呈現出跨天的議題分群）`==
            - sentiment_dict
                 >==`NTUSD 情緒字典`==
                - NTUSD_negative_unicode.txt
                - NTUSD_positive_unicode.txt
            - v0
                - v0_change_pronoun.py
                    >==`置換代名詞`==
                - v0_cluster_news.py
                    >==`BerTopic 新聞分群`==
                - v0_knn_cluster_news.py
                    >==`knn 新聞分群`== (不使用)
                - v0_cluster_opinions.py
                    >==`knn 同篇新聞意見分群`==
                - v0_find_opinions.py
                    >==`根據 NER 配對意見句`==
                - v0_sentiment_analyze.py
                    >==`利用 NTUSD 的情緒字典判斷正負意見`==
                - v0_person_unit_opinions.py
                    >==`新增「以人物為單位」的資料意見`==
                    >子任務包含
                    >1. 讀取原本的`person_unit_opinion.json`，並繼續**新增意見**
                    >2. 統一 `total_opinions.csv` 的人物名稱，以配對到正確的人物頁面
                    >3. 下載各個人物的圖片檔案
                    >4. 切片`person_unit_opinion.json`，再放到`crawler/result/fit_UI/person-slice-dataset`
                - :+1: **v0_run.py** 
                    >function 包含
                    >1. run_extraction ==`crawler + pre-processing + v0 演算法 呼叫中心`==
                    >2. fit_UI_format ==`檔案整理成 UI 需要的格式`==，目標資料夾在`crawler/result/fit_UI/`
    - pre-processing 
        - main.py
           >==`前處理整理中心`== 會被 `opinion/extract/v0/v0_run.py/run_extraction()`呼叫 
        - remove_space.py
            >==`去除空格`==
        - replace_comma.py
            >==`改變逗號`==
        - timestemp_convert.py
            >==`改變時間形式`==
    - UI
        - static
            >==`放置 css 檔案`==
            - front.css
            - list.css
            - opinions.css
        - templates
            >==`放置 html 檔案`==
            - dynamic_front.html
            - dynamic_list.html
            - dynamic_opinions.html
            - dynamic_person.html (也使用 opinions.css)
        - :+1: **app.py**
            >==`與使用者(網址)互動`== + ==`call opinion/extract/v0/v0_run.py`==

:100: :100: 最重要的兩個檔案就是
1. `opinion/extract/v0/v0_run.py`
2. `UI/app.py`

:a: 要注意任何檔案的相對位置，都應該要以 app.py 為準

