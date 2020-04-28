import requests
import json
import pandas as pd
import numpy as np

from config import QUERIES, DATA_SAVE_PATH
from os.path import join
from tqdm import tqdm
from lxml import html
from multiprocessing.pool import ThreadPool


tqdm.pandas()

def get_links_rbc(query):
    isfinal = False
    article_urls = []
    article_times = []
    article_titles = []
    offset = 0
    limit = 100

    while not isfinal:
        url = f'https://www.rbc.ru/v10/search/ajax/?query={query}&project=rbcnews|trends&offset={offset}&limit={limit}'

        # print(offset)
        article_meta = requests.get(url)
        article_meta = json.loads(article_meta.content)

        isfinal = len(article_meta['items']) < limit
        article_urls.extend([item['fronturl'] for item in article_meta['items']])
        article_times.extend(pd.to_datetime([item['publish_date'] for item in article_meta['items']]))
        article_titles.extend([item['title'] for item in article_meta['items']])

        offset += limit

    return pd.DataFrame({
        'article_url': article_urls,
        'article_time': article_times,
        'article_title': article_titles
    })


def extract_article_content_rbc(url):
    try:
        request = requests.get(url)
        page = html.fromstring(request.text)
        article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__text__overview", " " ))]//span | //p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])
        return article_content
    except:
        print(f'Cannot scrap: {url}')
        return np.nan

pool = ThreadPool()
df = pd.concat([get_links_rbc(q) for q in tqdm(QUERIES)]).drop_duplicates()
df['article_content'] = pool.map(extract_article_content_rbc, df.article_url.values)
df.to_csv(join(DATA_SAVE_PATH, 'rbc.csv'), index=False)