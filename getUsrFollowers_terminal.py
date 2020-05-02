# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:41 2019
@author: Taufik Sutanto
"""
import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau#, urllib3#, tweepy, sys
import time, numpy as np#, requests#, googlemaps, hashlib
#from urllib3.exceptions import InsecureRequestWarning
#from unidecode import unidecode
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import get_followers as gf
from tqdm import tqdm

if __name__ == '__main__':
    machine_id = 'BeeLink~getFollowers'
    nSleepA, nSleepB = 2, 5
    idle, maxIdle = 0, 33
    dbParF = {'db_': 'u8494347_twitter', 'tbl':'twitter_followers', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParTok = {'db_': 'u8494347_twitter', 'tbl':'tokens', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}

    tau.pyPriority() # set program priority to HIGH
    Ck, Cs, At, As = tau.getTokens(dbParTok, machine_id, key = None, status=1) #getToken, update status
    print('Getting twitter followers information ')
    while idle<maxIdle:
        try:
            screen_name, id_str = tau.getUsrFollow(dbParT, dbParF, key='screen_name', limit=1, idx=0, maxTry=3)
        except:
            print("Seems like we're finished :) wait = ", idle+1,'x')
            idle += 1; time.sleep(np.random.randint(nSleepA, nSleepB))
        screen_name = ''.join([d for d in screen_name if d.isalnum() or d=='_'])
        print('\nFinding followers of "{}"'.format(screen_name), flush=True)
        if id_str:
            id_usr = int(''.join([d for d in id_str.strip() if d.isdigit()]))
        else:
            id_usr = tau.getidusr(screen_name, dbParU, dbParT, Ck, Cs, At, As, dbParTok, machine_id) # get id_usr and all other information, update di twitter table and user table
        if screen_name and id_usr:
            try:
                #gf.get_followers(dbParF, screen_name, id_usr, Ck, Cs, At, As)
                gf.followers(screen_name, id_usr, dbParF,Ck, Cs, At, As)
            except:
                print("\nI have to sleep for a while ... ZZzzZzZZzzzz...")
                for i in tqdm(range(30)):
                    time.sleep(1)
                tau.getTokens(dbParTok, machine_id, key = At, status=0)
                Ck, Cs, At, As = tau.getTokens(dbParTok, machine_id, key = None, status=1) 
            tau.getTokens(dbParTok, machine_id, key = At, status=0)
            time.sleep(30)
            Ck, Cs, At, As = tau.getTokens(dbParTok, machine_id, key = None, status=1) 
        else:
            print('Seems like user {} is no longer in twitter database ...'.format(screen_name))
            qry = 'INSERT INTO {} (screen_name) VALUES ("{}")'.format(dbParF['tbl'], screen_name)
            tau.execSQL(dbParF, qry, maxTry=3)
    tau.getTokens(dbParTok, machine_id, key = At, status=0) #update status to 0