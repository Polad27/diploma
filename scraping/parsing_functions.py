import json
import requests
import pandas as pd
import locale
import os

from urllib.parse import urljoin
from tqdm import tqdm
from lxml import html
from lxml.etree import ParseError
locale.setlocale(locale.LC_TIME, 'rus_rus')



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
        article_title = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header__title", " " ))]')[0].text.strip()
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "time", " " ))]')[0].get('title')
        # article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header-author__name", " " ))]')[0].text.strip()
        article_content = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))] | '
                                     '//*[contains(concat( " ", @class, " " ), concat( " ", "content--full", " " ))]//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

        container_extended['article_url'].append(url)
        container_extended['article_time'].append(article_time)
        container_extended['article_title'].append(article_title)
        # container_extended['article_author'].append(article_author)
        container_extended['article_content'].append(article_content)

    except:
        print(f'Cannot scrap {url}')

    return container_extended


def collect_texts_tjornal(queries):
    link_list = []
    for query in queries:
        print(f'Getting links for query: {query}')
        link_list.extend(get_links_tjornal(query))

    container = {
        'article_url': [],
        'article_time': [],
        'article_title': [],
        # 'article_author': [],
        'article_content': []
    }

    print('Scraping websites')
    for url in tqdm(set(link_list)):
        container = extract_articles_tjornal(url, container)

    df = pd.DataFrame(container)
    df['article_time'] = df.article_time.str.slice(0, 16, 1)
    df.to_csv('tjornal.csv', index=False)


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


def extract_articles_meduza(url, container):
    container_extended = container.copy()
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

        container_extended['article_url'].append(url)
        container_extended['article_time'].append(article_time)
        container_extended['article_title'].append(article_title)
        # container_extended['article_author'].append(article_author)
        container_extended['article_content'].append(article_content)

    except:
        print(f'Cannot scrap: {url}')
        # raise Exception("Cannot scrap")
    return container_extended


def collect_texts_meduza(queries):

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

    link_list = []
    for query in queries:
        print(f'Getting links for query: {query}')
        link_list.extend(get_links_meduza(query))

    container = {
        'article_url': [],
        'article_time': [],
        'article_title': [],
        # 'article_author': [],
        'article_content': []
    }

    print('Scraping websites')
    for url in tqdm(set(link_list)):
        container = extract_articles_meduza(url, container)

    df = pd.DataFrame(container)
    tmp_df = df.article_time.str.split(' ', expand=True)
    tmp_df[2] = tmp_df[2].replace(months_dict)

    df['article_time'] = ''
    df['article_time'] = df['article_time'].str.cat(tmp_df, sep=' ')
    df['article_time'] = pd.to_datetime(df['article_time'], format=' %H:%M, %d %B %Y')
    df.to_csv('meduza.csv', index=False)


def get_links_nplus(query):
    search_page = html.fromstring(requests.get(f'https://nplus1.ru/search?q={query}').content)
    queried_urls = search_page.xpath('//*[(@id = "results")]//*[contains(concat( " ", @class, " " ), concat( " ", "caption", " " ))]')
    queried_urls = [urljoin('https://nplus1.ru', i.getparent().get('href')) for i in queried_urls]

    return queried_urls

def extract_articles_nplus(url, container):
    container_extended = container.copy()
    request = requests.get(url)
    page = html.fromstring(request.text)
    try:

        article_title = page.xpath('//h1')[0].text.strip()
        article_time = page.xpath('//time//span')[0].getparent().get('data-unix')
        # article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "MaterialNote-note_caption", " " ))]//strong')\
        #                      .text.strip()
        article_content = page.xpath('//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

        container_extended['article_url'].append(url)
        container_extended['article_time'].append(article_time)
        container_extended['article_title'].append(article_title)
        # container_extended['article_author'].append(article_author)
        container_extended['article_content'].append(article_content)

    except:
        print(f'Cannot scrap: {url}')
        # raise Exception("Cannot scrap")
    return container_extended

def collect_texts_nplus(queries):
    link_list = []
    for query in queries:
        print(f'Getting links for query: {query}')
        link_list.extend(get_links_nplus(query))
    container = {
        'article_url': [],
        'article_time': [],
        'article_title': [],
        # 'article_author': [],
        'article_content': []
    }

    print('Scraping websites')
    for url in tqdm(set(link_list)):
        container = extract_articles_nplus(url, container)

    df = pd.DataFrame(container)

    df['article_time'] = pd.to_datetime(df['article_time'], unit='s')
    df.to_csv('nplus.csv', index=False)


def get_links_village(query):
    n_pages = int(html.fromstring(requests.get(f'https://www.the-village.ru/search?query={query}').content)\
                  .xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "paginator", " " ))]')[0]\
                  .getchildren()[0].getchildren()[-1].text_content())
    print(n_pages)
    queried_urls = []
    for page_num in range(1, n_pages + 1):
        print(page_num)
        print(f'https://www.the-village.ru/search?query={query}&page={page_num}')
        search_page = html.fromstring(requests.get(f'https://www.the-village.ru/search?query={query}&page={page_num}').content)
        search_page_links = search_page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "post-link", " " ))]')
        queried_urls.extend([urljoin('https://www.the-village.ru', i.get('href'))  for i in search_page_links])

    return queried_urls


def extract_articles_village(url, container):
    container_extended = container.copy()
    request = requests.get(url)
    page = html.fromstring(request.text)
    try:

        article_title = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "RichTitle-root", " " ))] | '
                                  '//*[contains(concat( " ", @class, " " ), concat( " ", "SimpleTitle-root", " " ))]')[0] \
            .text.strip()
        article_time = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "Timestamp-root", " " ))]')[0] \
            .text.strip()
        # article_author = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "MaterialNote-note_caption", " " ))]//strong')\
        #                      .text.strip()
        article_content = page.xpath('//p')
        article_content = ' '.join([i.text.strip() for i in article_content if i.text is not None])

        container_extended['article_url'].append(url)
        container_extended['article_time'].append(article_time)
        container_extended['article_title'].append(article_title)
        # container_extended['article_author'].append(article_author)
        container_extended['article_content'].append(article_content)

    except:
        print(f'Cannot scrap: {url}')
        # raise Exception("Cannot scrap")
    return container_extended