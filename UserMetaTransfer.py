# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:41 2019
@author: Taufik Sutanto
"""
import taudata_crawl_tweet as tau
from tqdm import tqdm

if __name__ == '__main__':
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}

    tau.pyPriority() # set program priority to HIGH
    print('Moving some user information from tweet table to User Table ... ')
    qry = 'SELECT DISTINCT(screen_name), name, id_str, address, location, lat, lon FROM islam_id_2009_2019 WHERE screen_name NOT IN (SELECT screen_name FROM twitter_users)'
    db = tau.conMql(dbParT); cur = db.cursor()
    cur.execute(qry)
    data = cur.fetchall()
    cur.close();db.close()
    for d in tqdm(data):
        keys = ['screen_name', 'name', 'id_str', 'address', 'location', 'lat', 'lon']
        p = {k:v for k,v in zip(keys,d) if v}
        p = tau.sqlSafe(p)
        qry = tau.qryInsert(p, dbParU)
        try:
            tau.insertSQL(dbParU, qry, maxTry=1)
        except:
            pass