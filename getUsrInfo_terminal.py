# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:41 2019
@author: Taufik Sutanto

while TRUE
1. Query from bParT where nreplies is NULL
2. getInfo scrap 'date':wkt, 'nretweets':nRetweet, 'nreplies':nReplies, 'nlikes':nLikes
6. if error error_log table
"""
import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau, urllib3
import time, numpy as np, requests#, datetime#, pandas as pd, hashlib 
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if __name__ == '__main__':
    nSleepA, nSleepB = 3, 11
    idle, maxIdle = 0, 99
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    
    tau.pyPriority() # set program priority to HIGH
    print('Completing user information ... ')
    while idle<maxIdle:
        try:
            data = tau.getTweetInfo(dbParT, limit = 1, idx=0)
            if data:
                tweetID, url, username, date = data
                if date:
                    date = date.strftime('%Y-%m-%d')
                else:
                    date = datetime.today().strftime('%Y-%m-%d')
                print('Finding more information about ', username, ' on ', url)
                moreData = tau.getTweetsStat(url, date, headers = None)
                if moreData:
                    moreData['tweetID'] = tweetID
                    tau.updateTweet(moreData, dbParT)# {'date': '2020-01-18', 'nretweets': 53, 'nreplies': 2, 'nlikes': 74}
                    idle = 0 # reset counter
                else:
                    # ['date', 'nretweets', 'nreplies', 'nlikes']
                    print("I can't get more information :( ", url)
                    moreData = {'tweetID':tweetID, 'nretweets':0, 'nreplies':0, 'nlikes':0}
                    tau.updateTweet(moreData, dbParT)# {'date': '2020-01-18', 'nretweets': 53, 'nreplies': 2, 'nlikes': 74}
                    idle = 0 # reset counter
                time.sleep(np.random.randint(nSleepA, nSleepB))
            else:
                print("Seems like we're finished :) wait = ", idle+1,'x')
                idle += 1; time.sleep(np.random.randint(nSleepA, nSleepB))
        except:
            idle += 1; time.sleep(1)