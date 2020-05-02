# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 13:59:49 2020
Export Query to Database for better management and concurrency
@author: Taufik Sutanto
"""
import taudata_crawl_tweet as tau, hashlib
from tqdm import tqdm

if __name__ == '__main__':
    nSleepA, nSleepB, maxTry = 3, 11, 3
    y0, y1, lan = 2009, 2019, 'id'
    fQry = 'data/Queries_Islam_in_Media_Sosial.csv'
    dbParQ = {'db_': 'u8494347_twitter', 'tbl':'queries', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    waktu = tau.generateTimes(year_start = y0, year_end = y1)
    Queries = tau.loadQry(fQry, waktu, language=lan)
    
    for q in tqdm(Queries):
        Q = hashlib.md5(q.encode()).hexdigest()
        qry = "INSERT INTO {} (hashQry,qry) VALUES ('{}','{}')".format(dbParQ['tbl'],Q,q)
        db = tau.conMql(dbParQ); cur = db.cursor()
        cur.execute(qry)
        cur.close();db.close()
        