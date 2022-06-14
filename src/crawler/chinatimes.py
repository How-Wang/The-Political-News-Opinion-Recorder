import pathlib
from turtle import tiltangle
from warnings import catch_warnings
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_url_list(start_datetime, end_datetime)->list:
    
    NEWS_LIST_URL = 'https://www.chinatimes.com/politic/total?page={}&chdtv'
    TOTLE_PAGE = 50 # self defined page range # 10 original

    href_list = []

    # try:
    for page in range(1, TOTLE_PAGE + 1):
        url = f'https://www.chinatimes.com/politic/total?page={page}&chdtv'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        columns = soup.find_all("div", {"class": "col"})
        
        for e in columns:
            news_datetime = datetime.strptime(e.select_one('time')['datetime'], '%Y-%m-%d %H:%M')
            if news_datetime >= end_datetime:
                continue
            elif news_datetime < start_datetime:
                break
            else:
                href_list.append(e.select_one('a')['href'])
    return href_list

    # except:
    #     print('get_url_list error')
    #     return None

def get_xml(url_list):
    import util.status_code
    import util.normalize

    try:
        COMPANY_ID = util.normalize.get_company_id(company='中時')
        xml_list = []

        for url in url_list:
            url = 'https://www.chinatimes.com' + url
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
    import unicodedata
    import re
    BAD_ARTICLE_PATTERNS: List[re.Pattern] = [
    re.compile(r'文章來源:.*'),
    re.compile(r'----------------.*'),
    re.compile(r'更多內容.*'),
    re.compile(r'全文及圖表請見.*'),
    re.compile(r'圖片來源:.*'),
    re.compile(r'※免付費防疫專線.*'),
    re.compile(r' ★《中時新聞網》提醒您:'),
    re.compile(r' ★中時新聞網提醒您'),
]

    r"""Parse Chinatimes news from raw HTML."""
    # Information which cannot be parsed from `raw_xml`.
    
    try:
        soup = BeautifulSoup(raw_xml, 'html.parser')
    except Exception:
        raise ValueError('Invalid html format.')

    # News article.
    article = ''
    try:
        article_tags = soup.select('div.article-body > p')

        if article_tags:
            # Remove empty tags.
            article = ' '.join(
                filter(bool, map(lambda tag: tag.text.strip(), article_tags))
            )
        # One line only news. Chinatime is trash.
        else:
            article = soup.select('div.article-body')[0].text

        article = unicodedata.normalize('NFKC', article).strip()
        for pattern in BAD_ARTICLE_PATTERNS:
            search_result = pattern.search(article)
            if search_result:
                article = article[:search_result.start()]
                break
    except Exception:
        raise ValueError('Fail to parse Chinatimes news article.')

    # News category.
    category = ''
    try:
        category = soup.select(
            'nav.breadcrumb-wrapper > ol > li > a > span',
        )[-1].text
        category = unicodedata.normalize('NFKC', category).strip()
    except Exception:
        # There may not have category.
        category = ''

    # News datetime.
    timestamp = ''
    try:
        timestamp = datetime.strptime(
            soup.select('header.article-header time[datetime]')[0]['datetime'],
            '%Y-%m-%d %H:%M',
        )
        # Convert to UTC.
        timestamp = timestamp - timedelta(hours=8)
        timestamp = timestamp.timestamp()
    except Exception:
        # There may not have category.
        timestamp = ''

    # News reporter.
    reporter = ''
    try:
        reporter_tag = soup.select('div.author')[0]
        format_1 = reporter_tag.select('a')
        if format_1:
            reporter = format_1[0].text
        else:
            reporter = reporter_tag.text
        reporter = unicodedata.normalize('NFKC', reporter).strip()
    except Exception:
        # There may not have reporter.
        reporter = ''

    # News title.
    title = ''
    try:
        title = soup.select('h1.article-title')[0].text
        title = unicodedata.normalize('NFKC', title).strip()
    except Exception:
        raise ValueError('Fail to parse Chinatimes news title.')

    return article, category, timestamp, reporter, title




def crawler(start_datetime, end_datetime):
    for _ in range(3):
        print("Start to crawl Chinatimes news...")
        href_list = get_url_list(start_datetime, end_datetime)
        xml_list = get_xml(href_list)
        
        article_list = []
        category_list = []
        timestamp_list = []
        reporter_list = []
        title_list =  []
        
        for xml in xml_list:
            article, category, timestamp, reporter, title = parser(xml)
            article_list.append(article)
            category_list.append(category)
            timestamp_list.append(timestamp)
            reporter_list.append(reporter)
            title_list.append(title)
        
        if len(article_list) == 0:
            continue
        # for title, timestamp in zip(title_list, timestamp_list):
        #     timestamp = (datetime.fromtimestamp(timestamp) + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        #     print(title, timestamp)
        
        from util.csv import write_csv
        url_list = ['https://www.chinatimes.com' + i for i in href_list]
        company_list = ['中時'] * len(url_list)
        date_str = start_datetime.strftime('%Y-%m-%d')

        # 會從 app.py 的角度找檔案位置
        FILE_PATH = f'../crawler/result/raw/{date_str}_news/{date_str}_chinatimes.csv'
        pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        write_csv(FILE_PATH, timestamp_list, title_list, article_list, url_list, company_list, category_list, reporter_list)
        print(f'{date_str}_chinatimes.csv done!')
        break