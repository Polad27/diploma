import requests
import json
import locale
locale.setlocale(locale.LC_TIME, 'rus_rus')
import pandas as pd
from lxml import html
from parsing_functions import get_links_meduza
query = 'искусственный интеллект'
search_result = get_links_meduza(query)
print(search_result)

req = requests.get('https://tjournal.ru/flood/38909-amerikancy-ulichat-neyroseti-v-diskriminacii')
page = html.fromstring(req.text)

a = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "Timestamp-root", " " ))]')[0]
a

df = pd.read_csv('tjornal.csv')

page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content-header__title", " " ))]')[0].text.strip()

pd.to_datetime('19:03, 11 янв 2020', format='%H:%M, %d %b %Y')
a = pd.to_datetime('23.02.2020 19:30')
a.strftime("%d %b %Y %H:%M")