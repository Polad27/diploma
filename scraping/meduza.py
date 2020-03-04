# from scraping import parsing_functions as utils
import locale
import requests
import json
import pandas as pd
import numpy as np

from tqdm import tqdm
from lxml import html

tqdm.pandas()

locale.setlocale(locale.LC_TIME, 'rus_rus')
queries = ['искусственный интеллект', 'нейросети', 'машинное обучение']

months_dict = {
        'января': 'январь',
        'февраля': 'февраль',
        'марта': 'март',
        'апреля': 'апрель',
        'мая': 'май',
        'июня': 'июнь',
        'июля': 'июль',
        'августа': 'август',
        'сентября': 'сентябрь',
        'октября': 'октябрь',
        'ноября': 'ноябрь',
        'декабря': 'декабрь'
    }
# utils.collect_texts_meduza(queries)

def get_links_meduza(query):
    num_page = 0
    queried_urls = []
    has_next = True

    while has_next:
        try:
            # print('Page number: ', num_page)
            url = f'https://meduza.io/api/w5/search?term={query}&page={num_page}&per_page=100&locale=ru'
            request_js = json.loads(requests.get(url).content)
            queried_urls.extend([urljoin('https://meduza.io', i) for i in request_js['collection']])
            has_next = request_js['has_next']
            num_page += 1

        except ParseError as e:
            print(f'https://meduza.io/api/w5/search?term={query}&page={num_page}&per_page=100&locale=ru empty request')

    return pd.DataFrame({'article_url': queried_urls})


def extract_articles_meduza(url):
    request = requests.get(url)
    page = html.fromstring(request.text)
    try:
        article_title = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "RichTitle-root", " " ))] | '
                                  '//*[contains(concat( " ", @class, " " ), concat( " ", "SimpleTitle-root", " " ))]')[0]\
                           .text.strip()
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "Timestamp-root", " " ))]')[0]\
                           .text.strip()
        # article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "MaterialNote-note_caption", " " ))]//strong')\
        #                      .text.strip()
        article_content = page.xpath('//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

        return article_time, article_title, article_content

    except:
        print(f'Cannot scrap: {url}')
        # raise Exception("Cannot scrap")

months_dict = {
        'января': 'январь',
        'февраля': 'февраль',
        'марта': 'март',
        'апреля': 'апрель',
        'мая': 'май',
        'июня': 'июнь',
        'июля': 'июль',
        'августа': 'август',
        'сентября': 'сентябрь',
        'октября': 'октябрь',
        'ноября': 'ноябрь',
        'декабря': 'декабрь'
    }




    df = pd.DataFrame(container)
    tmp_df = df.article_time.str.split(' ', expand=True)
    tmp_df[2] = tmp_df[2].replace(months_dict)

    df['article_time'] = ''
    df['article_time'] = df['article_time'].str.cat(tmp_df, sep=' ')
    df['article_time'] = pd.to_datetime(df['article_time'], format=' %H:%M, %d %B %Y')
    df.to_csv('meduza.csv', index=False)

df = pd.concat([get_links_meduza(q) for q in tqdm(queries)]).drop_duplicates()
df['article_time'], df['article_title'], df['article_content'] = zip(*df.article_url.progress_apply(extract_articles_meduza))