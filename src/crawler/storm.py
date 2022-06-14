import pathlib
from bs4 import BeautifulSoup
import requests
import datetime
from datetime import datetime, timedelta


def get_url_list(start_datetime, end_datetime):

    NEWS_LIST_URL = 'https://www.storm.mg/category/118/'

    # title_list = []
    href_list = []
    # time_list = []
    for page in range(1, 20): # has 100 pages # oringal 10
        response = requests.get(NEWS_LIST_URL + str(page))
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = soup.find('div', {'class': 'category_cards_wrapper middle_category_cards'}).find_all('div', {'class': 'category_card card_thumbs_left'})
        
        for e in news_list:
            # print(e.find('h3', class_ = "card_title").text)
            # print(e.find('a', class_ = "card_link").get('href'))
            # print(e.find('span', class_ = "info_time").text)
            news_datetime = datetime.strptime(e.find('span', class_ = "info_time").text, '%Y-%m-%d %H:%M')
            if news_datetime >= end_datetime:
                continue
            elif news_datetime < start_datetime:
                break
            else:
            # title_list.append(e.find('h3', class_ = "card_title").text)
                href_list.append(e.find('a', class_ = "card_link").get('href'))
            # time_list.append(e.find('span', class_ = "info_time").text)
    return href_list

def get_xml_list(url_list):
    import util.status_code
    import util.normalize

    COMPANY_ID = util.normalize.get_company_id(company='風傳媒')
    xml_list = []

    for url in url_list:
        res = requests.get(url)
        
        util.status_code.check_status_code(
                company_id=COMPANY_ID,
                status_code=res.status_code,
                url=url,)

        raw_xml = util.normalize.compress_raw_xml(raw_xml=res.text)
        xml_list.append(raw_xml)
    
    return xml_list

def parser(raw_xml):
    """Parse STORM news from raw HTML.
    Input news must contain `raw_xml` and `url` since these information cannot
    be retrieved from `raw_xml`.
    """
    import re
    from datetime import datetime, timedelta
    from typing import List, Tuple

    from bs4 import BeautifulSoup

    from util import normalize
    # Information which cannot be parsed from `raw_xml`.
    # parsed_news = ParsedNews(
    #     url_pattern=raw_news.url_pattern,
    #     company_id=raw_news.company_id,
    # )
    ARTICLE_DECOMPOSE_LIST: str = re.sub(
    r'\s+',
    ' ',
    '''
    div#CMS_wrapper > blockquote,
    div#CMS_wrapper .related_copy_content,
    div#CMS_wrapper > p[aid] > .typeform-share link
    ''',
    )

    # News paragraphs are in the `div#CMS_wrapper p[aid]`.
    # Select the `p` tags with a `aid` attribute. But there is a case that articles
    # are wrapped in the `p[dir]` tag.
    # This observation is made with `url_pattern = 4031507`.
    ARTICLE_SELECTOR_LIST: str = re.sub(
        r'\s+',
        ' ',
        '''
        div#CMS_wrapper p[aid],
        div#CMS_wrapper p[dir]
        ''',
    )

    # Title is in `h1#article_title`.
    # This observation is made with `url_pattern = 4031976`.
    TITLE_SELECTOR_LIST: str = re.sub(
        r'\s+',
        ' ',
        '''
        h1#article_title
        ''',
    )

    ARTICLE_SUB_PATTERNS: List[Tuple[re.Pattern, str]] = [
        # Remove author information in the end of article. This observation is made
        # with `url_pattern = 4020745, 4029623`.
        (
            re.compile(r'\*?作者(?:為|:)?[\s\w]*?$'),
            '',
        ),
        # Remove the editor information. This observation is made with `url_pattern
        # = 4028800`.
        (
            re.compile(r'\s*(?:責任|採訪|編輯|後製|撰稿)?(?:採訪|編輯|後製|撰稿)[:/]\w*'),
            '',
        ),
        # Remove the source infomation. This observation is made with `url_pattern
        # = 21314, 26309`.
        (
            re.compile(r'\(?(?:資料|圖片)來源:[^\)]*\)?'),
            '',
        ),
        # Remove the url. This observation is made with `url_pattern = 21336,
        # 21679, 21680, 21747`.
        (
            re.compile(
                r'(?:《刺胳針》|研究|探險隊遠征)?(?:報告|直播)?(?:網址|網站)?[\s:]*?'
                + r'https?:\/\/[\(\)%\da-z\.-_\/-]+'
            ),
            '',
        ),
        # Remove the reporter. This observation is made with `url_pattern = 21680`.
        (
            re.compile(r'\d*?年?\d*?月?\d*?日?\s*?\w*?/綜合報導'),
            '',
        ),
        # Remove the extra information. This observation is made with
        # `url_pattern = 22241, 600064, 604069, 601210, 601348, 601417, 604783,
        # 604954, 612999, 620821`.
        (
            re.compile(
                r'(?:【前言】|-{4,}\s*|原文、圖經授權轉載自BBC中文網|報名網址\s*?\(\S*?\)|'
                + r'(?:更多精彩內容|文/\S*?|加入風運動|歡迎上官網|【立即購票】|' + r'本文經授權轉載自|[➤◎*]).*?$)'
            ),
            '',
        ),
    ]
    TITLE_SUB_PATTERNS: List[Tuple[re.Pattern, str]] = [
        # Remove fraction information. This observation is made with `url_pattern
        # = 22241, 26950, 600064, 603975, 612999, 629038, 629129`.
        (
            re.compile(
                r'([\(【](?:\d*?分?之\d*?|上|下|腦力犯中|下班經濟學)[\)】]|'
                + r'選摘\s*?\(\d*\)|^[\S\s]{,5}》)'
            ),
            '',
        ),
        # Remove separation symbol. This observation is made with `url_pattern
        # = 601417`.
        (
            re.compile(r'\|'),
            ' ',
        ),
    ]
    try:
        soup = BeautifulSoup(raw_xml, 'html.parser')
    except Exception:
        raise ValueError('Invalid html format.')

    ###########################################################################
    # Parsing news article.
    ###########################################################################
    article = ''
    try:
        list(
            map(
                lambda tag: tag.decompose(),
                soup.select(ARTICLE_DECOMPOSE_LIST),
            )
        )
        # Next we retrieve tags contains article text.  This statement must
        # always put after tags removing statement.
        article += ' '.join(
            map(
                lambda tag: tag.text,
                soup.select(ARTICLE_SELECTOR_LIST),
            )
        )
        article = normalize.NFKC(article)
    except Exception:
        raise ValueError('Fail to parse STORM news article.')

    ###########################################################################
    # Parsing news category.
    ###########################################################################
    category = ''
    try:
        # News category is always in the `div#title_tags_wrapper` tag. Since
        # there may be multiple `a` tags in the `title_tags_wrapper`, so we
        # use comma to concat them.
        category = normalize.NFKC(
            ','.join(
                map(
                    lambda tag: tag.text,
                    soup.select('div#title_tags_wrapper a')
                )
            )
        )
    except Exception:
        # There may not have category.
        category = ''

    ###########################################################################
    # Parsing news datetime.
    ###########################################################################
    timestamp = 0
    try:
        # News publishing date and time is always in the `span#info_time` tag.
        # We will convert datetime to POSIX time which is under UTC time zone.
        timestamp = datetime.strptime(
            soup.select('span#info_time')[0].text,
            '%Y-%m-%d %H:%M',
        )
        # Convert to UTC.
        timestamp = timestamp - timedelta(hours=8)
        timestamp = int(timestamp.timestamp())
    except Exception:
        # There may not have category.
        timestamp = 0

    ###########################################################################
    # Parsing news reporter.
    ###########################################################################
    reporter = ''
    try:
        # News reporter is always in `div#author_block span.info_author` tag.
        # 有些新聞來自其他新聞網站, reporter tag 會直接顯示該新聞來源, 如來自中央社的新聞,
        # `reporter` == '中央社'.
        # This observation is made with `url_pattern = 4034287`.
        reporter = normalize.NFKC(
            soup.select('div#author_block span.info_author')[0].text
        )
    except Exception:
        # There may not have reporter.
        reporter = ''

    ###########################################################################
    # Parsing news title.
    ###########################################################################
    title = ''
    try:
        title = ''.join(
            map(lambda tag: tag.text, soup.select(TITLE_SELECTOR_LIST))
        )
        title = normalize.NFKC(title)
    except Exception:
        # storm response 404 with status code 200.
        # Thus some pages do not have title since it is 404.
        raise ValueError('Fail to parse STORM news title.')

    ###########################################################################
    # Substitude some article pattern.
    ###########################################################################
    try:
        for article_pttn, article_sub_str in ARTICLE_SUB_PATTERNS:
            article = normalize.NFKC(
                article_pttn.sub(
                    article_sub_str,
                    article,
                )
            )
    except Exception:
        raise ValueError('Fail to substitude STORM article pattern.')

    ###########################################################################
    # Substitude some title pattern.
    ###########################################################################
    try:
        for title_pttn, title_sub_str in TITLE_SUB_PATTERNS:
            title = normalize.NFKC(
                title_pttn.sub(
                    title_sub_str,
                    title,
                )
            )
    except Exception:
        raise ValueError('Fail to substitude STORM title pattern.')

    return article, category, reporter, timestamp, title


def crawler(start_datetime, end_datetime):
    import datetime
    from datetime import timedelta, datetime
    for _ in range(3):
        print("Start to crawl STORM news...")
        href_list = get_url_list(start_datetime, end_datetime)
        xml_list = get_xml_list(href_list)
        
        article_list = []
        category_list = []
        reporter_list = []
        timestamp_list = []
        title_list =  []
        
        for xml, url in zip(xml_list, href_list):
            article, category, reporter, timestamp, title = parser(xml)
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
        date_str = start_datetime.strftime('%Y-%m-%d')
        company_list = ['風傳媒'] * len(href_list)

        FILE_PATH = f'../crawler/result/raw/{date_str}_news/{date_str}_storm.csv'
        pathlib.Path(FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        write_csv(FILE_PATH, timestamp_list, title_list, article_list, href_list, company_list, category_list, reporter_list)
        print(f'{date_str}_storm.csv done!')
        break