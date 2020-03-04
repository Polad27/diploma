import requests
import json
import pandas as pd

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
    request = requests.get(url)
    page = html.fromstring(request.text)
    try:
        article_title = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header__title", " " ))]')[0].text.strip()
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "time", " " ))]')[0].get('data-date')
        # article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header-author__name", " " ))]')[0].text.strip()
        article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))] | '
                                     '//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))]//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])
        return article_time, article_title, article_content
    except:
        print(f'Cannot scrap {url}')



df = pd.concat([get_links_tjornal(q) for q in tqdm(queries)]).drop_duplicates()
df['article_time'], df['article_title'], df['article_content'] = zip(*df.article_url.progress_apply(extract_articles_tjornal))
df['article_time'] = df.article_time.astype(int)
df.to_csv('../data/tjornal.csv', index=False)
# def collect_texts_tjornal(queries):
#     link_list = []
#     for query in queries:
#         print(f'Getting links for query: {query}')
#         link_list.extend(get_links_tjornal(query))
#
#     container = {
#         'article_url': [],
#         'article_time': [],
#         'article_title': [],
#         # 'article_author': [],
#         'article_content': []
#     }
#
#     print('Scraping websites')
#     for url in tqdm(set(link_list)):
#         container = extract_articles_tjornal(url, container)
#
#     df = pd.DataFrame(container)
#     df['article_time'] = df.article_time.str.slice(0, 16, 1)
#     df.to_csv('tjornal.csv', index=False)
request = requests.get('https://tjournal.ru/news/138980-issledovanie-tolko-tret-rossiyan-ponimayut-sut-iskusstvennogo-intellekta')
page = html.fromstring(request.text)
