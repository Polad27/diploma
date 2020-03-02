import pandas as pd
from tqdm import tqdm
def read_data(files, dropna=True, drop_duplicates=None, **kwargs):
    df = pd.concat([pd.read_csv(f, **kwargs) for f in files])
    if dropna:
        df.dropna(inplace=True)
    if drop_duplicates is not None:
        df.drop_duplicates(subset=drop_duplicates, inplace=True)

    return  df

def remove_stopwords(texts, stop_words):
    return [[word for word in text if word not in stop_words] for text in texts]

def make_bigrams(texts, bigram_model):
    return [bigram_model[text] for text in texts]

def lemmatization(texts, lemm_object):
    """https://spacy.io/api/annotation"""
    texts_out = [lemm_object.lemmatize(' '.join(text)) for text in tqdm(texts)]
    return texts_out