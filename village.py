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

import parsing_functions as utils

req = requests.get('https://www.the-village.ru/search?query=искусственный интеллект')
page = html.fromstring(req.content)
a = page.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "paginator", " " ))]')
len(a)

a[0].get('href')
utils.get_links_village('нейросети')