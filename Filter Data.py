# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:09:18 2020
1. Load Data Tweet "D" [select tweet_id, tweet, screen_name, address]
2. Load Data Labeled
2. Whitelists screen_names where kategori !=0
3. Whitelist all mentions by whitelist 1
4. Whitelist all contain "indonesia" di address atau location
5. Whitelist all tweets by bahasa:
    A. Preprocess D
    B. for d in D:
        pe = [True for i in d.split() if d in Ce])
        pi = [True for i in d.split() if d in Ci])
        po = kalau len(pe) & pi <3 dan len(D)>5 ==> po
    C. if len(prob_i)>len(prob_e):
        D[i] = False
    D. Update language di tabel Tweet
6. Save whitelisted users
@author: Taufik Sutanto
"""

import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau#, urllib3#, tweepy, sys
import pandas as pd, numpy as np, seaborn as sns #requests, time
from scipy import stats
#import taudata as tau2

if __name__ == '__main__':
    gKey = 'AIzaSyBjW1wJtX8ca_KrpzIvL8mWZJcsEBU-fZY'
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParG = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    file_label = 'data/Tweet_Labels.csv'
    data = pd.read_csv(file_label, error_bad_lines=False, low_memory = False)
    names = ['Iim', 'Yani', 'Endi', 'Fahmi', 'Aziz', 'Dita']
    cols = ['tweetID', 'screen_name', 'tweet']
    #for name in names:
    #    data[name] = data[name].astype('int64')
    #print(data.dtypes)
    dt = {}
    dt['tweetID'], dt['screen_name'], dt['tweet'], dt['label'] = [], [], [], []
    for i, d in data.iterrows():
        #break
        scores = []
        for name in names:
            try:
                scores.append(int(d[name]))
            except:
                pass
        scores.sort(reverse = True)
        try:
            mode, freq = stats.mode(scores)
            mode = mode[0]
        except:
            mode = 0
        if mode>5:
            mode = 0
        dt['label'].append(mode)
        for c in cols:
            dt[c].append(d[c])
    dt = pd.DataFrame.from_dict(dt)    
    print(dt['label'].value_counts())
    
    print('loading corpus english & indonesian ...')
    ce = tau.enCorpus(lan = 'en')
    ci = tau.enCorpus(lan = 'id')
    