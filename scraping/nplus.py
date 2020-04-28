import requests
import pandas as pd
import locale

import numpy as np

from urllib.parse import urljoin
from tqdm import tqdm
from lxml import html
from config import QUERIES, DATA_SAVE_PATH
from os.path import join

tqdm.pandas()

locale.setlocale(locale.LC_TIME, 'rus_rus')

def get_links_nplus(query):
    search_page = html.fromstring(requests.get(f'https://nplus1.ru/search?q={query}').content)
    queried_urls = search_page.xpath('//*[(@id = "results")]//*[contains(concat( " ", @class, " " ), concat( " ", "caption", " " ))]')
    queried_urls = [urljoin('https://nplus1.ru', i.getparent().get('href')) for i in queried_urls]

    return pd.DataFrame({'article_url': queried_urls})

def extract_articles_nplus(url):
    request = requests.get(url)
    page = html.fromstring(request.text)
    try:
        article_title = page.xpath('//h1')[0].text.strip()
        article_time = page.xpath('//time//span')[0].getparent().get('data-unix')
        # article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "MaterialNote-note_caption", " " ))]//strong')\
        #                      .text.strip()
        article_content = page.xpath('//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])
        return article_time, article_title, article_content
    except:
        print(f'Cannot scrap: {url}')
        # raise Exception("Cannot scrap")
        return np.nan, np.nan, np.nan

df = pd.concat([get_links_nplus(q) for q in tqdm(QUERIES)]).drop_duplicates()
df['article_time'], df['article_title'], df['article_content'] = zip(*df.article_url.progress_apply(extract_articles_nplus))
df['article_time'] = pd.to_datetime(df['article_time'], unit='s')
df.to_csv(join(DATA_SAVE_PATH, 'nplus.csv'), index=False)