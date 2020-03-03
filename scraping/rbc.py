import requests
import json
import pandas as pd

from lxml import html



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

        isfinal = len(js['items']) < limit
        article_urls.extend([item['fronturl'] for item in js['items']])
        article_times.extend(pd.to_datetime([item['fronturl'] for item in js['items']]))
        offset += limit

req = requests.get('https://www.rbc.ru/search/?query=искусственный интеллект&project=rbcnews|trends')
page = html.fromstring(req.content)
len(page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "search-item__title", " " ))]'))

isfinal = False
search_results = []
offset = 0
limit = 100
while not isfinal:
    print(offset)
    req2 = requests.get(f'https://www.rbc.ru/v10/search/ajax/?query=искусственный интеллект&project=rbcnews|trends&offset={offset}&limit={limit}')
    js = json.loads(req2.content)
    isfinal = len(js['items']) < limit
    search_results.extend([item['id'] for item in js['items']])
    offset += limit

len(js['items'])
pd.to_datetime(js['items'][0]['publish_date'])