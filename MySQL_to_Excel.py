# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 06:20:56 2020

@author: taufi
"""
import taudata_crawl_tweet as tau
import taudata as tau2
import pandas as pd
from tqdm import tqdm
from textblob import TextBlob
from sklearn.datasets import fetch_20newsgroups
from nltk.corpus import brown
from sklearn.feature_extraction.text import CountVectorizer

if __name__ == '__main__':
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParG = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    fTweets = 'data/islam_id_2009_2019.xlsx'
    
    print('Querying from Database ... \nTweets, ')
    db = tau.conMql(dbParT)
    # SELECT * FROM `islam_id_2009_2019` WHERE isretweet=0 AND length(tweet) > 100 AND tweet NOT LIKE '%@%'
    query = "SELECT tweetID, screen_name, nretweets, tweet FROM {} WHERE isretweet=0 AND length(tweet) > 100 AND tweet NOT LIKE '%@%'".format(dbParT['tbl'])
    df1 = pd.read_sql(query, db)   
    
    
    print('Loading some corpus: ', end='')
    corpus = tau.enCorpus(lan = 'en')
    data = {}
    data['tweetID'], data['screen_name'], data['nretweets'], data['tweet'] = [], [], [], []
    for i, r in tqdm(df1.iterrows()):
        if i>26000:
            doc = tau2.cleanText(r.tweet, symbols_remove = True, min_charLen = 3, max_charLen = 12, fixTag= True, fixMix=True)
            tokens = [str(t).lower().strip() for t in TextBlob(doc).words if str(t) in corpus]
            """
            try:
                b = TextBlob(str(doc)).detect_language()
            except:
                b = ''
            """
            if len(tokens)<5: # and b!='en':
                data['tweetID'].append(r.tweetID)
                data['screen_name'].append(r.screen_name)
                data['nretweets'].append(r.nretweets)
                data['tweet'].append(r.tweet)
    print('Saving {} data to Excel ...'.format(len(data)))
    data = pd.DataFrame.from_dict(data)
    """     
    print('Users ...')
    query = "SELECT * FROM {}".format(dbParU['tbl'])
    df2 = pd.read_sql(query, db)
    print('Locations ... ')
    query = "SELECT * FROM {}".format(dbParG['tbl'])
    df3 = pd.read_sql(query, db)
    db.close()
    #df.to_csv(fTweets, encoding='utf-8', index=False)
    """
    
    with pd.ExcelWriter(fTweets) as writer:  # doctest: +SKIP
        print('tweets, ', end='')
        #df1.to_excel(writer, sheet_name='tweets')
        data.to_excel(writer, sheet_name='tweets')
        #print('users information, ', end='')
        #df2.to_excel(writer, sheet_name='users')
        #print('places.')
        #df3.to_excel(writer, sheet_name='places')
    print('\nAll Done.')
