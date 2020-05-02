# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:09:18 2020
1. Load Corpus Bhs Indonesia & Bahasa Inggris Ci Ce
2. Load Data Tweet "D" [tweet dan tweet ID]
3. Preprocess D
4. for d in D:
    prob_e = [True for i in d.split() if d in Ce])
    prob_i = [True for i in d.split() if d in Ci])
5. if len(prob_i)>len(prob_e):
    D[i] = False
6. Filtered data "data" = [ (d, tweetID) for d in D if d]
7. Save saja dulu ke CSV datanya JANGAN update database, bahaya 
8. CAUTION BACKUP DULU!!!!.... 
@author: Taufik Sutanto
"""

import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau#, urllib3#, tweepy, sys
import googlemaps, hashlib #requests, time, numpy as np,  
#from unidecode import unidecode


if __name__ == '__main__':
    gKey = 'AIzaSyBjW1wJtX8ca_KrpzIvL8mWZJcsEBU-fZY'
    nSleepA, nSleepB = 2, 7
    locDefault = 'indonesia'
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParG = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    
    
    