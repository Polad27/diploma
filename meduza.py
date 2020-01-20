import parsing_functions as utils
import locale
import pandas as pd

locale.setlocale(locale.LC_TIME, 'rus_rus')
queries = ['искусственный интеллект', 'нейросети', 'машинное обучение']
utils.collect_texts_meduza(queries)
