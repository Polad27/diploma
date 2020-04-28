import requests
import pandas as pd

from os.path import join
from tqdm import tqdm
from config import QUERIES, DATA_SAVE_PATH


def extract_articles_lenta(query, retrieve_size=500):
    url = f'https://m.lenta.ru/search/v2/process?from=0&size=2&sort=2&title_only' \
          f'=0&domain=1&modified%2Cformat=yyyy-MM-dd&query={query}'
    total_found = requests.get(url).json()['total_found']
    fields_mapper = {
        'url': 'article_url',
        'pubdate': 'article_time',
        'title': 'article_title',
        'text': 'article_content'
    }
    dfs = []
    for i in range(int(total_found/retrieve_size)+1):
        tmp_url = f'https://m.lenta.ru/search/v2/process?from={retrieve_size*i}&size={retrieve_size}&sort=2&title_only' \
                  f'=0&domain=1&modified%2Cformat=yyyy-MM-dd&query={query}'
        dfs.append(pd.DataFrame.from_dict(requests.get(tmp_url).json()['matches'])[list(fields_mapper.keys())])

    return pd.concat(dfs).rename(columns=fields_mapper)

df = pd.concat([extract_articles_lenta(q) for q in tqdm(QUERIES)]).drop_duplicates()
df.to_csv(join(DATA_SAVE_PATH, 'lenta.csv'), index=False)