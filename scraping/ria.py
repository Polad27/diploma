import requests
import pandas as pd
import locale

import numpy as np

from urllib.parse import urljoin, urlencode, quote_plus
from tqdm import tqdm
from lxml import html
from config import QUERIES, DATA_SAVE_PATH
from os.path import join

tqdm.pandas()

def get_links_ria(query):
    query = quote_plus(query)
    links = []
    total_found_page = html.fromstring(requests.get(f'https://ria.ru/search/?query={query}').text)
    total_found = int(total_found_page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "m-active", " " ))]//span')[0].text)
    # offset = 0
    for i in tqdm(range(int((total_found)/20 + 1))):
        url = f'https://ria.ru/services/search/getmore/?query={query}&offset={20*i}'
        page = html.fromstring(requests.get(url).text)
        queried_urls = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "color-font-hover-only", " " ))]')
        links.extend([link.get('href') for link in queried_urls if 'radiosputnik' not in link.get('href')])
        # n_links = len(queried_urls)
        # offset += n_links

    return pd.DataFrame({'article_url': links})


def extract_articles_ria(url):
    try:
        page = html.fromstring(requests.get(url).text)
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__info-date", " " ))]//a')[0].text
        article_title = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__title", " " ))]')[0].text
        article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article__text", " " ))]')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

        return article_time, article_title, article_content
    except Exception:
        # print(e)
        return np.nan, np.nan, np.nan


df = pd.concat([get_links_ria(q) for q in QUERIES]).drop_duplicates()
df['article_time'], df['article_title'], df['article_content'] = zip(*df.article_url.progress_apply(extract_articles_ria))
df['article_time'] = pd.to_datetime(df.article_time)
df.to_csv('../data/ria.csv', index=False)
# df.to_csv(join(DATA_SAVE_PATH, 'ria.csv'), index=False)