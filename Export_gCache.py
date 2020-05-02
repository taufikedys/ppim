# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:05:35 2020
Test Export Lat Lon Location ke Google Cache 
@author: taufi
"""
import pymysql as pyOld, time, hashlib
from tqdm import tqdm
import mysql.connector as pymysql
from unidecode import unidecode
import taudata_crawl_tweet as tau



if __name__ == '__main__':
    dbG = {'db_': 'stunting', 'tbl':'gcache', 'usr':'root', 'pas':'x1234', 'hst':'localhost'}
    dbGw = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    print('Loading Data from localhost ... ')
    db = pymysql.connect(host=dbG['hst'], user=dbG['usr'], passwd=dbG['pas'], db=dbG['db_'])
    cur = db.cursor()
    cur.execute("SELECT location, lat, lon FROM twitter WHERE lat!=0.0 OR lon!=0.0")
    row = cur.fetchall()
    cur.close(); db.close()
    print('loaded "{}" rows of data'.format(len(row)))
    print('incrementally put in cloud ...')
    
    for area, loc, lat, lon in tqdm(row):
        qry = tau.qryGcache(area, loc, lat, lon, dbGw)
        try:
            ins = tau.insgCache(dbGw, qry, maxTry=3)
        except:
            pass
