import requests
import json
import unicodedata as unicode
import re
import pandas as pd
import locale

from tqdm import tqdm
from lxml import html


tqdm.pandas()



queries = ['искусственный интеллект', 'нейросети', 'машинное обучение']


def get_links_tjornal(query):
    is_finished = False
    num_page = 1
    queried_urls = []

    while not is_finished:
        try:
            # print('Page number: ', num_page)
            url = f'https://tjournal.ru/search_ajax/v2/{query}/content/relevant/{num_page}'
            request_js = json.loads(requests.get(url).content)
            search_results = html.fromstring(request_js['data']['feed_html'])\
                                 .xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-feed__link", " " ))]')
            queried_urls.extend([i.get('href') for i in search_results])
            is_finished = request_js['data']['is_finished']
            num_page += 1

        except ParseError as e:
            print(f'https://tjournal.ru/search_ajax/v2/{query}/content/relevant/{num_page} empty request')

    return pd.DataFrame({'article_url': queried_urls})



def extract_articles_tjornal(url):

    months_dict = {
        'янв': 'Jan',
        'фев': 'Feb',
        'мар': 'Mar',
        'апр': 'Apr',
        'май': 'May',
        'июн': 'Jun',
        'июл': 'Jul',
        'авг': 'Aug',
        'сен': 'Sep',
        'окт': 'Oct',
        'ноя': 'Nov',
        'дек': 'Dec',
        'мая': 'May'
    }

    request = requests.get(url)
    page = html.fromstring(request.text)

    article_title = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header__title", " " ))]')[0].text.strip()
    try:
        article_time = int(page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "time", " " ))]')[0].get('data-date'))
        print(article_time)
    except:
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "time", " " ))]')[0].text
        article_time = unicode.normalize('NFKD', article_time).split(' ')
        article_time[1] = months_dict[article_time[1]]
        article_time = pd.to_datetime(' '.join(article_time)).value * 10**-9
        print(article_time, pd.to_datetime(article_time, unit='s'))

    article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))] | '
                                 '//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))]//p')
    article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

    return article_time, article_title, article_content



df = pd.concat([get_links_tjornal(q) for q in tqdm(queries)]).drop_duplicates()
df['article_time'], df['article_title'], df['article_content'] = zip(*df.article_url.progress_apply(extract_articles_tjornal))
df['article_time'] = pd.to_datetime(df.article_time, unit='s')
df.to_csv('./data/tjornal.csv', index=False)
