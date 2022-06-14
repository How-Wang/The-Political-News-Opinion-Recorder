# The Political News Opinion Recorder
**政事意見新聞紀錄簿** 
## Introduction  
📰 以事件群、議題為單位，整合各家媒體所釋出的資訊  
🗣️ 視覺化人物發言呈現、整理單篇新聞內的文章，輔以情緒分析  
📈 最後利用議題分類、人物判斷，貫穿時間軸，直接看出政治人物長期的意見變化！
## Strength
|     | 傳統政治新聞                   | 政事新聞意見紀錄簿             |
| --- | -------------------------- | ------------------------------ |
|數量| ❌動輒數百篇，數量龐大     | ✔️新聞議題分群，讀最關鍵的新聞 |
|內容| ❌純文字文章結構，難以閱讀 | ✔️視覺化人物發言，輔以情緒分析 |
|時間| ❌分日單篇，無法追蹤政治人物意見 |✔️以議題與政治人物為單位，貫穿時間軸追蹤|

## Architecture
![](https://i.imgur.com/0fxN3Tu.png)
1. 先爬下多家網路媒體的新聞，進行前處理，把多餘的空格去除，方便後續任務的執行。
2. 執行 `Name Entity Recognition` ，找出文章中的專有名詞，並去除時間、數量值等等比較沒有利用價值的專有名詞，以利後續統計出分群關鍵字。
3. 根據剛剛得到的專有名詞，自行建立一個人名字典，把文章中裡面出現的人物單名根據字典做統一的代換。
4. 接著任務分成兩部分，一個為分群任務，另一個為意見擷取。
5. 分群任務先利用 `BERTopic` 對文章進行分群，但因為時間維度要做到長期的議題追蹤，所以再根據已經分完群的當日議題，使用 `sentence-transformer` 以 `ckiplab/bert-base-chinese` 為 `embedder` 再做一次 `KNN` 分群，如此一來，我們就可以知道哪幾天的哪些事件是屬於同一個議題，做到跨天的分類。
6. 在意見提取的部分，使用兩種方式做驗測，第一個是使用 `CKIPCoreNLP Toolkit Parsing Tree`；另一個為利用自行建立的動詞字典，再搭配`Name Entity Recognition` 找出動主詞配對。
7. 為了避免意見重複出現在同一篇文章中，接著一樣再使用第五點提到的 `KNN` 分群，把相似度高的意見去除。
8. 意見提取完後，以 `NTUSD` 情緒字典 比較擷取出來的意見，作為判斷正負情緒的依據。
9. 最後根據需要的 UI 模式，調整檔案形式，並自行設定自動化爬取、以 `Flask` 為框架，將系統架設在 `Google Cloud Platform` 以供閱聽者使用。
## Website Demo
- [🔗 Website Link](http://34.80.42.37:5000/)
1. **首頁呈現新聞分群結果**
![image](https://user-images.githubusercontent.com/62500402/173529497-df0451b3-35d0-49fb-ada7-a025aac95841.png)
    
2. **新聞分群列表**
![](https://i.imgur.com/MWJaCxx.png)
   
3. **單篇新聞人物視覺化**
![image](https://user-images.githubusercontent.com/62500402/173530055-33cd1fe8-0536-4bf8-90e6-e2fb0c84a111.png)
![](https://i.imgur.com/XCVcvjd.png)
    
4. **政治人物議題長期追蹤**
![](https://i.imgur.com/ywQBISA.png)
![](https://i.imgur.com/vBDzn0U.png)

## Implementation

```shell
# create an environment
# platform: win-64
$ conda create --name <env> --file requirements.txt

# under path ..\src\UI\
$ python app.py
```

## Analysis
    
### Different Version
|           | 動詞選擇                     | 主詞選擇                                 |
| --------- | ---------------------------- | ---------------------------------------- |
| version 0 | 手動建立動詞字典              | 動詞往前之特定條件下的第一個專有名詞     |
| version 1 | Parsing Tree VE2             | 與動詞屬同一句子的 agent，且結構為一對一 |
| version 2 | Parsing Tree VE2 + VC + VE11 | 與動詞屬同一句子的 agent，且結構不限     |

![](https://i.imgur.com/proLALS.png)

### Score

|           | precision | recall    | f1        |
| --------- | --------- | --------- | --------- |
| version 0 | ***0.689*** | 0.521     | 0.575     |
| version 1 | 0.679     | 0.518     | 0.569     |
| version 2 | 0.609     | ***0.699*** | ***0.639*** |

（使用100篇手動標記 ettoday 政治新聞意見做驗證）
## Contributor
### Author / Maintainers
- [@Howard](https://github.com/How-Wang)
- [@TCHuang](https://github.com/tc-huang)
### Reference
- [CKIP CoreNLP Toolkit](https://github.com/ckiplab/ckipnlp)
- [BERTopic](https://github.com/MaartenGr/BERTopic)
- [sentence-transformer](https://github.com/UKPLab/sentence-transformers)
- [IKMLab/Taiwan_news_dataset](https://github.com/IKMLab/Taiwan_news_dataset)
