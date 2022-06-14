import pathlib
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager

def get_url_list(start_datetime, end_datetime):


    NEWS_LIST_URL = 'https://www.setn.com/ViewAll.aspx?PageGroupID=6'

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(5)
    driver.get(NEWS_LIST_URL)
    driver.implicitly_wait(5)

    for _ in range(30): # has more than 30 pages # oringal 10
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()

    news_list = soup.find('div', {'class': 'row NewsList'}).find_all('div', {'class': 'col-sm-12 newsItems'})

    # tilte_list = []
    herf_list = []
    # time_list = []
    
    for e in news_list:
        # print(e.find('a', class_="gt").get('href'))
        # print(e.find('a', class_="gt").text)
        # print(e.find('time').text)
        news_datetime = datetime.strptime(e.find('time').text, '%m/%d %H:%M')
        news_datetime = news_datetime.replace(year=start_datetime.year)
        if news_datetime >= end_datetime:
                continue
        elif news_datetime < start_datetime:
            break
        else:
        # tilte_list.append(e.find('a', class_="gt").text)
            herf_list.append(e.find('a', class_="gt").get('href'))
        # time_list.append(e.find('time').text)
    return herf_list

def get_xml_list(url_list):
    import util.status_code
    import util.normalize
    import requests

    try:
        COMPANY_ID = util.normalize.get_company_id(company='三立')
        xml_list = []

        for url in url_list:
            url = 'https://www.setn.com' + url
            res = requests.get(url)
            util.status_code.check_status_code(
                    company_id=COMPANY_ID,
                    status_code=res.status_code,
                    url=url,)

            raw_xml = util.normalize.compress_raw_xml(raw_xml=res.text)
            xml_list.append(raw_xml)
        
        return xml_list

    except:
        print('get_xml error')
        return None




def parser(raw_xml):
    """Parse SET news from raw HTML.
    Input news must contain `raw_xml` and `url` since these information cannot
    be retrieved from `raw_xml`.
    """
    # Information which cannot be parsed from `raw_xml`.
    # parsed_news = ParsedNews(
    #     url_pattern=raw_news.url_pattern,
    #     company_id=raw_news.company_id,
    # )
    import re
    import unicodedata
    CATEGORIES = {
    0: '熱門',
    2: '財經',
    4: '生活',
    5: '國際',
    6: '政治',
    7: '科技',
    8: '娛樂',
    9: '名家專欄',
    12: '汽車',
    17: '華流',
    34: '運動',
    41: '社會',
    42: '新奇',
    45: '日韓',
    46: '音樂',
    47: '寵物',
    50: '旅遊',
    52: '女孩',
    54: '房產',
    65: '健康',
    }

    END_ARTICLE_PATTERNS = [
        re.compile(r'※ 免付費防疫專線.*'),
    ]

    REPORTER_PATTERNS = [
        re.compile(r'^記者(.*?)/.*?報導'),
        re.compile(r'^.*?/(.*?)報導'),
        re.compile(r'^影音編輯/(.*?) '),
        re.compile(r'^助理編輯/(.*?) '),
    ]
    try:
        soup = BeautifulSoup(raw_xml, 'html.parser')
    except Exception:
        raise ValueError('Invalid html format.')

    # News article.
    article = ''
    try:
        article_tags = soup.select(
            'div#Content1 > p:not([class]):not([style])',
        )
        # Joint remaining text.
        article = ' '.join(
            filter(
                bool,
                map(lambda tag: tag.text.strip(), article_tags),
            )
        )
        article = unicodedata.normalize('NFKC', article).strip()
        for pattern in END_ARTICLE_PATTERNS:
            search_result = pattern.search(article)
            if search_result:
                article = article[:search_result.start()]
                break
        article = article.strip()
    except Exception:
        raise ValueError('Fail to parse SET news article.')

    # News category.
    category = ''
    try:
        category = CATEGORIES[soup.select(
            'input[type=hidden]#pageGroupID, input[type=hidden]#hfPageGroupId'
        )[0]['value']]
        category = unicodedata.normalize('NFKC', category).strip()
    except Exception:
        # There may not have category.
        category = ''

    # News datetime.
    timestamp = 0
    try:
        time_tag = soup.select('time.page-date')[0]
        timestamp = datetime.strptime(time_tag.text, '%Y/%m/%d %H:%M:%S')
        # Convert to UTC.
        timestamp = timestamp - timedelta(hours=8)
        timestamp = timestamp.timestamp()
    except Exception:
        # There may not have category.
        timestamp = 0

    # News reporter.
    reporter = ''
    try:
        for pattern in REPORTER_PATTERNS:
            match = pattern.match(article)
            if match:
                reporter = ','.join(match.groups())
                article = article[:match.start()] + article[match.end():]
                article = article.strip()
                break
    except Exception:
        # There may not have reporter.
        reporter = ''

    # News title.
    title = ''
    try:
        title = soup.select('h1.news-title-3')[0].text
        title = unicodedata.normalize('NFKC', title).strip()
    except Exception:
        raise ValueError('Fail to parse SET news title.')

    return article, category, reporter, timestamp, title

def crawler(start_datetime, end_datetime):
    from datetime import timedelta
    for _ in range(3):
        print("Start to crawl SET news...")

        href_list = get_url_list(start_datetime, end_datetime)
        xml_list = get_xml_list(href_list)
        
        article_list = []
        category_list = []
        reporter_list = []
        timestamp_list = []
        title_list =  []
        
        for xml in xml_list:
            article, category, reporter, timestemp, title = parser(xml)
            article_list.append(article)
            category_list.append(category)
            reporter_list.append(reporter)
            timestamp_list.append(timestemp)
            title_list.append(title)
        
        if len(article_list) == 0:
            continue
        # for title, timestamp in zip(title_list, timestamp_list):
        #     timestamp = (datetime.fromtimestamp(timestamp) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        #     print(title, timestamp)

        from util.csv import write_csv
        url_list = ['https://www.setn.com' + url for url in href_list]
        company_list = ['三立'] * len(url_list)
        date_str = start_datetime.strftime('%Y-%m-%d')

        FILE_PATH = f'../crawler/result/raw/{date_str}_news/{date_str}_stn.csv'
        pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        write_csv(FILE_PATH, timestamp_list, title_list, article_list, url_list, company_list, category_list, reporter_list)
        print(f'{date_str}_stn.csv done!')
        break