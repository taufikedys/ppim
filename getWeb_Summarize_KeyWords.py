# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:47:12 2020

@author: Taufik Sutanto
"""
import warnings; warnings.simplefilter('ignore')
import taudata_web as tau, requests
import pandas as pd
from urllib.request import Request, urlopen
from urllib3.exceptions import InsecureRequestWarning
import urllib3
from gensim.summarization import summarize, keywords
from tqdm import tqdm
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

nKeyWords = 20
fWeb = 'data/Web_List_All_Category.csv'
fResult = 'data/Web_List_Summarized.csv'
print('loading data: ', fWeb, flush = True)
W = pd.read_csv(fWeb, error_bad_lines=False, low_memory = False)
W = W.URL.to_list()
W = [w.lower().strip() for w in W]

fSlang = 'data/slang.dic'
stops, lemma = tau.LoadStopWords(lang='id')
fix = tau.loadCorpus(file = fSlang, sep=':')
headers = tau.getHeaders()

Result = {'url':[], 'keywords':[], 'summary':[]}
for i, url in tqdm(enumerate(W)):
    print('Scraping, summarizing, and getting keywords from:\n', url)
    try:
        req = Request(url, headers = headers) 
        doc = urlopen(req).read()
        doc = tau.text_from_html(doc)
        clean_web = tau.cleanText(doc, fix=fix, lemma=lemma, stops = stops, min_charLen = 2, max_charLen = 12, fixTag= False, fixMix=True)
        S = summarize(doc, split=True, ratio=0.1)
        K = keywords(clean_web).split('\n')[:nKeyWords]
        Result['url'].append(url)
        Result['keywords'].append(K)
        Result['summary'].append(S)
    except:
        pass 
    
print('Done, ... saving to:', fResult)
df = pd.DataFrame.from_dict(Result)
df.to_csv(fResult, encoding='utf-8', index=True)
print('All finish...')
