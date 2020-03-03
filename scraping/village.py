import requests
import locale

from lxml import html

locale.setlocale(locale.LC_TIME, 'rus_rus')

from scraping import parsing_functions as utils

req = requests.get('https://www.the-village.ru/search?query=искусственный интеллект')
page = html.fromstring(req.content)
a = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "paginator", " " ))]')
len(a[0][0][-1])

a[0].get('href')
utils.get_links_village('нейросети')