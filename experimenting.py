import requests
import json
import locale
import re
locale.setlocale(locale.LC_TIME, 'rus_rus')
import pandas as pd
from lxml import html
from parsing_functions import get_links_meduza
query = 'искусственный интеллект'
search_result = get_links_meduza(query)
print(search_result)

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

req = requests.get('https://meduza.io/feature/2020/01/16/meduzoid-iz-serdtsa-krysy-i-kiborgi-iz-lyagushachiey-ikry')
page = html.fromstring(req.text)

a = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "Timestamp-root", " " ))]')[0]
re.sub(f"({'|'.join(months_dict.keys())})", a.text.strip())

df = pd.read_csv('tjornal.csv')

page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header__title", " " ))]')[0].text.strip()

pd.to_datetime('19:03, 11 январь 2020', format='%H:%M, %d %B %Y')
a = pd.to_datetime('23.02.2020 19:30')
a.strftime("%d %b %Y %H:%M")


container = {
    'article_url': [],
    'article_time': [],
    'article_head': [],
    'article_author': [],
    'article_content': []
}

df = pd.read_csv('meduza.csv', parse_dates=['article_time'])
df.head()
df.shape