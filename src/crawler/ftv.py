import pathlib
from bs4 import BeautifulSoup
import requests
import datetime
from datetime import timedelta, datetime


def get_url_list(start_datetime, end_datetime):
    NEWS_LIST_URL = 'https://www.ftvnews.com.tw/tag/%E6%94%BF%E6%B2%BB/'

    # title_list = []
    href_list = []
    time_list = []

    for page in range(1, 20):   # limit to 55 # original 5
        response = requests.get(NEWS_LIST_URL + str(page))
        soup = BeautifulSoup(response.text, "html.parser")

        news_list = soup.find_all('li', class_='col-lg-4 col-sm-6')
        
        for e in news_list:
            # # print(e.find('h2').text)
            # # print(e.select_one('.time').text)
            # # print(e.find('a').get('href'))
            # title_list.append(e.find('h2').text)
            news_datetime = datetime.strptime(e.select_one('.time').text, '%Y/%m/%d %H:%M:%S')
            if news_datetime >= end_datetime:
                continue
            elif news_datetime < start_datetime:
                break
            else:
                href_list.append(e.find('a').get('href'))
                time_list.append((news_datetime - timedelta(hours=8)).timestamp())
    
    return href_list, time_list

def get_xml_list(url_list):
    import util.status_code
    import util.normalize

    try:
        COMPANY_ID = util.normalize.get_company_id(company='民視')
        xml_list = []

        for url in url_list:
            url = 'https://www.ftvnews.com.tw' + url
            res = requests.get(url)
            
            util.status_code.check_status_code(
                    company_id=COMPANY_ID,
                    status_code=res.status_code,
                    url=url,)

            raw_xml = util.normalize.compress_raw_xml(raw_xml=res.text)
            xml_list.append(raw_xml)
        
        return xml_list

    except:
        print('get_xml_list error')
        return None

def parser(raw_xml, url):
    import unicodedata
    import re
    """Parse FTV news from raw HTML.
    Input news must contain `raw_xml` and `url` since these information cannot
    be retrieved from `raw_xml`.
    """
    # Information which cannot be parsed from `raw_xml`.
    # parsed_news = ParsedNews(
    #     url_pattern=raw_news.url_pattern,
    #     company_id=raw_news.company_id,
    # )
    REPORTER_END_PATTERNS = [
    re
    .compile(r'[。!\s]\s*\(.{0,6}/([^(綜合|整理)]{0,16})\s+.{0,4}(:?報導|編輯)\){0,2}'),
    re.compile(r'[。!\s]\s*.{0,6}/([^(綜合|整理)]{0,16})\s*.{0,4}(:?報導|編輯)'),
    re.compile(r'\(責任編輯/(.*?)\)'),
    # (民視新聞/鄭博暉、林俊明、洪明生 台南-屏東)
    re.compile(r'[。!\s]\s*\(.{0,6}/([^(綜合|整理)]{0,16})\s+.{0,10}\){0,2}'),
    ]

    REPORTER_BEGIN_PATTERNS = [
        re.compile(r'^【.{0,6}\s+([^(綜合|整理)]*?)/.{0,4}(:?報導|編輯)】'),
        re.compile(r'^【.{0,6}/記者([^(綜合|整理)]*?)(:?報導|編輯)】'),
        re.compile(r'^.{0,6}/([^(綜合|整理)]{0,10})(:?報導|編輯)'),
    ]

    BAD_TITLE_PATTERNS = [
        re.compile(r'MLB/'),
        re.compile(r'P\.LEAGUE\+/'),
        re.compile(r'法網/'),
        re.compile(r'快新聞/'),
        re.compile(r'→'),
        re.compile(r'LIVE/'),
        re.compile(r'NBA/'),
        re.compile(r'影/'),
        re.compile(r'有影/'),
    ]

    BAD_ARTICLE_PATTERNS = [
        re.compile(r'^.{0,6}/(.{0,10})(:?報導|編輯)'),
        re.compile(r'文章轉載自:.*'),
        re.compile(r'文章授權:.*'),
        re.compile(r'延伸閱讀:.*'),
        re.compile(r'【延伸閱讀】.*'),
        re.compile(r'更多古典樂新訊息:.*'),
        re.compile(r'\(中央社\)'),
        re.compile(r'影片轉載自:.*'),
        re.compile(r'\(民視新聞(網)?[\s/]綜合報導\)'),
        re.compile(r'\(\w*?報導\)'),
        re.compile(r'※ 免付費防疫專線:.*'),
        re.compile(r'更多最新消息.*'),
        re.compile(r'就❤NOW健康:.*'),
        re.compile(r'《(:?民視快新聞|民視新聞網)》提醒您:.*'),
        re.compile(r'更多NOW健康報導.*'),
        re.compile(r'★.*'),
        re.compile(r' ◆ .*'),
        re.compile(r'更多精彩的詳細影片:.*'),
        re.compile(r'全部照片,請見臉書社團.*'),
        re.compile(r'所有精彩節目內容.*'),
        re.compile(r'❤?【NOW健康】關心您:.*'),
        re.compile(r'現場最新情形請鎖定《民視快新聞》直播.*'),
        re.compile(r'-{5,}.*?-{5,}'),
        re.compile(r'【看更多】.*'),
        re.compile(r'・'),
        re.compile(r'民視新聞網關心您.*'),
    ]

    CATEGORIES = {
        'A': '體育',
        'C': '一般',
        'F': '財經',
        'I': '國際',
        'J': '美食',
        'L': '生活',
        'N': '社會',
        'P': '政治',
        'R': '美食',
        'S': '社會',
        'U': '社會',
        'W': '一般',
    }
    try:
        soup = BeautifulSoup(raw_xml, 'html.parser')
    except Exception:
        raise ValueError('Invalid html format.')

    # News article.
    article = ''
    try:
        article_tags = soup.select('div#preface > p, div#newscontent > p')
        article = ' '.join(p_tag.text.strip() for p_tag in article_tags)
        article = unicodedata.normalize('NFKC', article).strip()
    except Exception:
        raise ValueError('Fail to parse FTV news article.')
    # News category.
    category = ''
    try:
        category_word = url.split('/')[-1][7]
        category = CATEGORIES[category_word]
    except Exception:
        # There may not have category.
        category = ''

    # News datetime.
    timestamp = 0
    try:
        url_datetime = url('/')[-1][:7]
        url_datetime = f'{url_datetime[:4]}' + \
            f'{int("0x" + url_datetime[4], 0):02}{url_datetime[5:]}'
        timestamp = datetime.strptime(
            url_datetime,
            '%Y%m%d',
        )
        timestamp = timestamp.timestamp()
    except Exception:
        # There may not have category.
        timestamp = 0

    # News reporter.
    reporter = ''
    try:
        for pattern in REPORTER_BEGIN_PATTERNS:
            match = pattern.match(article)
            if match:
                reporter = match.group(1).strip()
                article = article[match.end():].strip()
                break
        if not reporter:
            for pattern in REPORTER_END_PATTERNS:
                match = pattern.search(article)
                if match:
                    reporter = match.group(1).strip()
                    article = article[:match.start()].strip()
                    break

    except Exception:
        # There may not have reporter.
        reporter = ''

    # Filter article bad pattern.
    try:
        for pattern in BAD_ARTICLE_PATTERNS:
            article = pattern.sub('', article)
        article = re.sub(r'\s+', ' ', article).strip()

        # If article is not end with period.
        if article and not re.match('[。!?]', article[-1]):
            article = article + '。'
    except Exception:
        raise ValueError('Fail to parse FTV news article.')

    # News title.
    title = ''
    try:
        title = soup.select('div.col-article > h1.text-center')[0].text
        title = unicodedata.normalize('NFKC', title).strip()
        for pattern in BAD_TITLE_PATTERNS:
            match = pattern.search(title)
            if match:
                title = title[:match.start()] + title[match.end():]
    except Exception:
        # FTV response 404 with status code 200.
        # Thus some pages do not have title since it is 404.
        raise ValueError('Fail to parse FTV news title.')

    return article, category, reporter, timestamp, title

def crawler(start_datetime, end_datetime):
    from datetime import datetime
    for _ in range(3): 

        print("Start to crawl FTV news...")
        href_list, time_list = get_url_list(start_datetime, end_datetime)
        xml_list = get_xml_list(href_list)
        
        article_list = []
        category_list = []
        reporter_list = []
        title_list =  []
        timestamp_list = time_list
        
        for xml, url in zip(xml_list, href_list):
            article, category, reporter, timestamp, title = parser(xml, url)
            article_list.append(article)
            category_list.append(category)
            reporter_list.append(reporter)
            title_list.append(title)
        
        if len(article_list) == 0:
            continue
        
        # for title, timestamp in zip(title_list, timestamp_list):
        #     timestamp = (datetime.fromtimestamp(timestamp) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        #     print(title, timestamp)

        from util.csv import write_csv
        url_list = ['https://www.ftvnews.com.tw' + url for url in href_list]
        date_str = start_datetime.strftime('%Y-%m-%d')
        company_list = ['民視'] * len(url_list)

        FILE_PATH = f'../crawler/result/raw/{date_str}_news/{date_str}_ftv.csv'
        pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        write_csv(FILE_PATH, timestamp_list, title_list, article_list, url_list, company_list, category_list, reporter_list)
        print(f'{date_str}_ftv.csv done!')
        break