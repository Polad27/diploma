import requests
import json
import pandas as pd
import numpy as np

from tqdm import tqdm
from lxml import html


tqdm.pandas()

def get_links_rbc(query):
    isfinal = False
    article_urls = []
    article_times = []
    article_titles = []
    offset = 0
    limit = 100

    while not isfinal:
        print(offset)
        article_meta = requests.get(f'https://www.rbc.ru/v10/search/ajax/?query={query}&project=rbcnews|trends&offset={offset}&limit={limit}')
        article_meta = json.loads(article_meta.content)

        isfinal = len(article_meta['items']) < limit
        article_urls.extend([item['fronturl'] for item in article_meta['items']])
        article_times.extend(pd.to_datetime([item['publish_date'] for item in article_meta['items']]))
        article_titles.extend([item['title'] for item in article_meta['items']])

        offset += limit

    return pd.DataFrame({
        'article_urls': article_urls,
        'article_times': article_times,
        'article_titles': article_titles
    })


def extract_articles_rbc(url):
    request = requests.get(url)
    page = html.fromstring(request.text)

    try:
        article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__text__overview", " " ))]//span | //p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])
        return article_content
    except:
        print(f'Cannot scrap: {url}')
        return np.nan

df = get_links_rbc('искусственный интеллект')
df = df.loc[~df.article_urls.str.startswith('https://pro.rbc')]
df['article_content'] = df.iloc[:100].article_urls.progress_apply(extract_articles_rbc)
df.article_content.values[0]
df['lol'], df['kek'], df['azaza'] = zip(*df.article_urls.apply(lambda x: (np.random.randint(10, 20), np.random.randint(40, 80), np.random.randint(-20, -10))))

df.head()