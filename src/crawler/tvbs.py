import pathlib
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

def get_url_list(start_datetime, end_datetime):


    NEWS_LIST_URL = 'https://news.tvbs.com.tw/politics'

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(5)
    driver.get(NEWS_LIST_URL)
    driver.implicitly_wait(5)

    for _ in range(5):  # has more than 5
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()

    news_list = soup.find('div', class_='news_now2').find_all('li')

    # title_list = []
    href_list = []
    # time_list = []

    for e in news_list:
        # print(e.find('h2').text)
        # print(e.select('.time')[0].text)
        # print(e.find('a')['href'])
        news_datetime = datetime.strptime(e.select('.time')[0].text, '%Y/%m/%d %H:%M')
        if news_datetime >= end_datetime:
                continue
        elif news_datetime < start_datetime:
            break
        else:
        # title_list.append(e.find('h2').text)
            href_list.append(e.find('a')['href'])
        # time_list.append(e.select('.time')[0].text)

    return href_list

def get_xml_list(url_list):
    import util.status_code
    import util.normalize
    import requests

    try:
        COMPANY_ID = util.normalize.get_company_id(company='tvbs')
        xml_list = []

        for url in url_list:
            url = 'https://news.tvbs.com.tw' + url
            res = requests.get(url)
            if res.status_code == 200:
                xml_list.append(res.text)
            else:
                print(res.status_code)
                print(url)
    except:
        print(url)
        pass
    return xml_list

def parser(raw_xml, url):
    """Parse TVBS news from raw HTML.
    Input news must contain `raw_xml` and `url` since these information cannot
    be retrieved from `raw_xml`.
    """
    import re
    import unicodedata
    from datetime import timedelta

    import bs4
    import dateutil.parser
    from bs4 import BeautifulSoup
    # Information which cannot be parsed from `raw_xml`.
    # parsed_news = ParsedNews(
    #     url_pattern=raw_news.url_pattern,
    #     company_id=raw_news.company_id,
    # )
    DROP_ARTICLE_PATTERNS = [
    re.compile(r'因應新冠肺炎疫情，疾管署持續疫情監測與邊境管制措施，'),
    re.compile(r'◎\s*本文摘自'),
    re.compile(r'◎\s*圖片來源'),
    re.compile(r'〈首圖出處'),
    re.compile(r'《TVBS》提醒您'),
    ]

    REMOVE_ARTICLE_PATTERNS = [
        re.compile(r'（中央社）'),
        re.compile(r'最HOT話題在這！想跟上時事，快點我加入TVBS新聞LINE好友！'),
        re.compile(
            r'《TVBS》提醒您：因應新冠肺炎疫情，疾管署持續疫情監測與邊境管制措施，如有疑似症狀，請撥打：1922專線，或 0800-001922。'
        ),
        re.compile(r'(?:實習)?編輯／.*?$'),
    ]

    CATEGORIES = {
        'local': '社會',
        'life': '生活',
        'world': '國際',
        'entertainment': '娛樂',
        'china': '中國',
        'politics': '政治',
        'sports': '運動',
        'tech': '科技',
        'focus': '焦點',
        'fun': '新奇',
        'travel': '旅遊',
        'health': '健康',
        'cars': '車',
        'money': '財經',
    }
    CATEGORY_PATTERN = re.compile(r'/(.*?)/\d+')

    try:
        soup = BeautifulSoup(raw_xml, 'html.parser')
    except Exception:
        raise ValueError('Invalid html format.')

    # News article.
    article = ''
    try:
        article_node = soup.select('div#news_detail_div > html > body')[0]
        # Discard image, caption and related news.
        for tag in article_node.select('div.img, div[style], span.endtext, b'):
            tag.extract()

        # # Strong tags and styled text.
        # for tag in article_node.select('span[style], strong'):

        # Get remaining text.
        for node in article_node.children:
            if isinstance(node, bs4.element.Tag):
                text = node.text
            else:
                text = str(node)

            # Drop following text if pattern matched.
            for pattern in DROP_ARTICLE_PATTERNS:
                drop_pattern_match = pattern.match(text)
                if drop_pattern_match:
                    text = ''
                    break

            if drop_pattern_match:
                break

            # Remove text if pattern matched.
            for pattern in REMOVE_ARTICLE_PATTERNS:
                text = pattern.sub('', text)

            if text:
                article += text + ' '

        article = unicodedata.normalize('NFKC', article).strip()
    except Exception:
        raise ValueError('Fail to parse TVBS news article.')

    # News category.
    category = ''
    try:
        category = CATEGORIES[CATEGORY_PATTERN.match(
            url,
        ).group(1)]
        category = unicodedata.normalize('NFKC', category).strip()
    except Exception:
        # There may not have category.
        category = ''

    # News datetime.
    timestamp = 0
    try:
        # Convert to UTC.
        timestamp = dateutil.parser.isoparse(
            soup.select('meta[name=pubdate]')[0]['content']
        ) - timedelta(hours=8)
        timestamp = timestamp.timestamp()
    except Exception:
        # There may not have category.
        timestamp = 0

    # News reporter.
    reporter = ''
    try:
        reporter = soup.select('div.author_box > div.author > a')[0].text
        reporter = unicodedata.normalize('NFKC', reporter).strip()
    except Exception:
        # There may not have reporter.
        reporter = ''

    # News title.
    title = ''
    try:
        title = soup.select('div.title_box > h1.title')[0].text
        title = unicodedata.normalize('NFKC', title).strip()
    except Exception:
        # storm response 404 with status code 200.
        # Thus some pages do not have title since it is 404.
        raise ValueError('Fail to parse TVBS news title.')

    return article, category, reporter, timestamp, title

def crawler(start_datetime, end_datetime):

    from datetime import datetime
    from datetime import timedelta
    for _ in range(3):
        print("Start to crawl TVBS news...")

        href_list = get_url_list(start_datetime, end_datetime)
        xml_list = get_xml_list(href_list)

        article_list = []
        category_list = []
        reporter_list = []
        timestamp_list = []
        title_list =  []
        
        for xml, url in zip(xml_list, href_list):
            article, category, reporter, timestamp, title = parser(xml, url)
            article_list.append(article)
            category_list.append(category)
            reporter_list.append(reporter)
            timestamp_list.append(timestamp)
            title_list.append(title)
        
        if len(article_list) == 0:
            continue
        # for title, timestamp in zip(title_list, timestamp_list):
        #     timestamp = (datetime.fromtimestamp(timestamp) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        #     print(title, timestamp)

        from util.csv import write_csv
        url_list = ['https://news.tvbs.com.tw' + url for url in href_list]
        company_list = ['TVBS'] * len(url_list)
        date_str = start_datetime.strftime('%Y-%m-%d')

        FILE_PATH = f'../crawler/result/raw/{date_str}_news/{date_str}_tvbs.csv'
        pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        write_csv(FILE_PATH, timestamp_list, title_list, article_list, url_list, company_list, category_list, reporter_list)
        print(f'{date_str}_tvbs.csv done!')
        break