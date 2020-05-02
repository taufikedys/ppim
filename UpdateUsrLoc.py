# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:41 2019
@author: Taufik Sutanto
"""
import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau#, urllib3#, tweepy, sys
import googlemaps, hashlib #requests, time, numpy as np,  
#from unidecode import unidecode
"""

NEED to Be resumable!!!.....

Method 2:
1. Select distinct location from Tabel tweet where address is not null
    SELECT distinct(LOWER(location)) FROM `islam_id_2009_2019` WHERE location IS NOT NULL
2. Loop check ada/tidak location di gCache yg address is not null
    jika tidak:
        Look in gmaps ==> get address, lat, lon
    jika address, lat, lon:
2. Update semua entity di table user where lower(location) = location_1
3. Do the same to Tweet Table

"""

if __name__ == '__main__':
    gKey = 'AIzaSyBjW1wJtX8ca_KrpzIvL8mWZJcsEBU-fZY'
    nSleepA, nSleepB = 2, 7
    locDefault = 'indonesia'
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParG = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    
    tau.pyPriority() # set program priority to HIGH
    print('Updating user Location information ... ')
    data = tau.getLocations(dbParT)
    if data:
        print('Updating {} number of unique locations'.format(len(data)))
        for i, d in enumerate(data):
            print('{}/{} Location = "{}"'.format(i+1, len(data), d[0]), end = ', ', flush=True)
            if i>2311:
                location = d[0]
                hashLocation = hashlib.md5(location.encode()).hexdigest()
                address_latLon = tau.checkLatLon(dbParG, hashLocation, key='hash_location')
                if address_latLon:
                    print('exist in gTable', end = ', ')
                    address, lat, lon = address_latLon['address'], address_latLon['lat'], address_latLon['lon']
                else:
                    print('searching in gMap', end = ', ')
                    #not exist in gCache
                    gmaps = googlemaps.Client(key=gKey)
                    lat, lon, address = tau.getPlace(gmaps, location, lan='id')
                    del gmaps
                    # UPDATE table gCache
                    print('updating gMap', end = ', ')
                    p = {'location':location, 'address':address, 'lat':lat, 'lon':lon}
                    p = tau.sqlSafe(p)
                    qry = tau.qryGcache(p, dbParG)
                    tau.insertSQL(dbParG, qry, maxTry=3)
                if address and lat and lon:
                    # exist further information of the location
                    # update table tweet
                    print('updating Tweet Table', end = ', ')
                    p = {'location':location, 'address':address, 'lat':lat, 'lon':lon}
                    qry = tau.qryUpdate(dbParT, p, key = 'location')
                    qry = qry.replace('location', 'LOWER(location)')
                    res = tau.execSQL(dbParT, qry, maxTry=3)
                    # Update Table user
                    print('updating User Table')
                    qry = tau.qryUpdate(dbParU, p, key = 'location')
                    qry = qry.replace('location', 'LOWER(location)')
                    res = tau.execSQL(dbParU, qry, maxTry=3)
                else:
                    print()
            else:
                    print()
                