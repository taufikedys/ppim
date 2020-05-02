# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:41 2019
@author: Taufik Sutanto
    * Filter berdasarkan nama akun atau if "word" in status
    * Topic Modelling: tanpa retweet
    * Viral : retweet included     
"""
import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau, urllib3 # sys,
import time, numpy as np#, hashlib # pandas as pd, 
import requests#, subprocess, sys#, mysql.connector as pymysql
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getTweet(qry, lan=None, headers=None, nSleepA=1, nSleepB=5, maxTry=3):
    try_ = 0
    while try_<maxTry:
        try:
            return tau.getTweets(qry, lan = lan, headers = headers)
        except:
            print("Something wrong, I'm gonna try again ... ")
            try_ += 1; time.sleep(np.random.randint(nSleepA, nSleepB))

if __name__ == '__main__':
    nSleepA, nSleepB, maxTry = 3, 11, 3
    lan, maxCrawl = 'id', 100
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParQ = {'db_': 'u8494347_twitter', 'tbl':'queries', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}

    tau.pyPriority() # set program priority to HIGH
    count, machineID = 0, 1
    while count<33:
        id_, qry, hashQry = tau.getQry(machineID, dbParQ, maxTry=3) # get uRl, update machineID, TImeStamp, dan status to 1
        #if qry:
        if qry and '2019' in qry: # WARNING this is just to Update
            print('\nquery #{} = \n"{}"'.format(id_, qry))
            posts, next_ = getTweet(qry, lan=lan, headers=None, nSleepA=nSleepA, nSleepB=nSleepB, maxTry=maxTry)
            if posts:
                tau.insertTweet(posts, dbParT, maxTry=3)
                if next_:
                    page = 1; print('\nPage ', end='')
                    while next_ and page <= maxCrawl:
                        print('"{}"'.format(page), end=', ')
                        try:
                            posts, next_ = getTweet(next_, lan=lan, headers=None, nSleepA=nSleepA, nSleepB=nSleepB, maxTry=maxTry)                
                            if posts:
                                tau.insertTweet(posts, dbParT, maxTry=3)
                        except:
                            next_ = None; break
                        page += 1
                        time.sleep(np.random.randint(nSleepA, nSleepB))
            tau.updateQry(hashQry, dbParQ, maxTry=3) # status to 2
            count = 0 # reset counter
            """
            if page>=maxCrawl:
                subprocess.call(['getTweet.bat'])
                sys.exit('Refreshing MySelf ... ')
            """
        else:
            tau.updateQry(hashQry, dbParQ, maxTry=3) # # WARNING this is just to Update
            print('\nPassed on query #{} = \n"{}"'.format(id_, qry))
            #count += 1; print('count = ', count)
    print("\nFinished initial Scrapping for Tweets")