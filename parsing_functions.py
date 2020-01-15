import json
import requests
import pandas as pd
import os


from urllib.parse import urljoin
from tqdm import tqdm
from lxml import html
from lxml.etree import ParseError

def get_links_tjornal(query):
    is_finished = False
    num_page = 1
    queried_urls = []

    while not is_finished:
        try:
            print('Page number: ', num_page)
            url = f'https://tjournal.ru/search_ajax/v2/{query}/content/relevant/{num_page}'
            request_js = json.loads(requests.get(url).content)
            search_results = html.fromstring(request_js['data']['feed_html'])\
                                 .xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-feed__link", " " ))]')
            queried_urls.extend([i.get('href') for i in search_results])
            is_finished = request_js['data']['is_finished']
            num_page += 1

        except ParseError as e:
            print(f'https://tjournal.ru/search_ajax/v2/{query}/content/relevant/{num_page} empty request')
    return queried_urls



def extract_articles_tjornal(url, container):
    container_extended = container.copy()
    request = requests.get(url)
    page = html.fromstring(request.text)
    try:
        article_head = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header__title", " " ))]')[0].text.strip()
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "time", " " ))]')[0].get('title')
        article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header-author__name", " " ))]')[0].text.strip()
        article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))] | //*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))]//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

        container_extended['article_url'].append(url)
        container_extended['article_time'].append(article_time)
        container_extended['article_head'].append(article_head)
        container_extended['article_author'].append(article_author)
        container_extended['article_content'].append(article_content)

        return container_extended
    except:
        print(url)
        raise Exception("Cannot scrap")




def collect_texts_tjornal(queries):
    link_list = []
    for query in queries:
        print(f'Getting links for query: {query}')
        link_list.extend(get_links_tjornal(query))

    container = {
        'article_url': [],
        'article_time': [],
        'article_head': [],
        'article_author': [],
        'article_content': []
    }

    for url in tqdm(link_list):
        container = extract_articles_tjornal(url, container)

    pd.DataFrame(container).to_csv('tjornal.csv', index=False)

def get_links_meduza(query):
    num_page = 0
    queried_urls = []
    has_next = True

    while has_next:
        try:
            print('Page number: ', num_page)
            url = f'https://meduza.io/api/w5/search?term={query}&page={num_page}&per_page=100&locale=ru'
            request_js = json.loads(requests.get(url).content)
            queried_urls.extend([urljoin('https://meduza.io', i) for i in request_js['collection']])
            has_next = request_js['has_next']
            num_page += 1

        except ParseError as e:
            print(f'https://meduza.io/api/w5/search?term={query}&page={num_page}&per_page=100&locale=ru empty request')
    return queried_urls