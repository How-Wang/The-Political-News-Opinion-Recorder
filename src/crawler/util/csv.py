import csv
import pandas as pd

def write_csv(path, timestamp, title, article, url, company, category, reporter):
    dict = {'timestamp': timestamp, 'title': title, 'article': article, 'url': url, 'company': company, 'category': category, 'reporter': reporter}
    df = pd.DataFrame(dict)
    df.to_csv(path, index=False)