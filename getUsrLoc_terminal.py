# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:41 2019
@author: Taufik Sutanto
"""
import warnings; warnings.simplefilter('ignore')
import taudata_crawl_tweet as tau#, urllib3#, tweepy, sys
import time, numpy as np, googlemaps, hashlib #requests, 
from unidecode import unidecode
"""
Method 2:
1. Select distinct location where address is not null
2. Update semua entity di table user where location = location_1
3. Do the same to Tweet Table

Method 1:
1. Select location from table user where location is null or location = '--' ==> cari lat lon address
2. update semua dengan lokasi yg sama di table user
3. update semua di table tweet

Method 3:
1. Select distinct locations from table tweet
2. if not in gCache cari address, lat, lon -nya
3. Lakukan Method 2 
4. Method 1 jadi obsolete

"""


if __name__ == '__main__':
    machine_id = '720S~getLocations'
    gKey = 'AIzaSyBjW1wJtX8ca_KrpzIvL8mWZJcsEBU-fZY'
    
    nSleepA, nSleepB = 15, 30
    idle, maxIdle = 0, 17
    locDefault = 'indonesia'
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParG = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParTok = {'db_': 'u8494347_twitter', 'tbl':'tokens', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    
    Ck, Cs, At, As = tau.getTokens(dbParTok, machine_id, status=1) #getToken, update status
    tau.pyPriority() # set program priority to HIGH
    print('Completing user Location information ... ')
    while idle<maxIdle:
        data = tau.getNoAreaUsr(dbParT)
        if data:
            tweetID, url, screen_name, id_str, name = data
            pu = {'screen_name': screen_name}
            print('\nFinding more information about {} a.k.a. {}'.format(screen_name, name))
            
            d = tau.getUsrDetails(screen_name, Ck,Cs,At,As, dbParTok, machine_id, maxTry = 3)
            keys = ['name', 'description', 'id_str', 'followers_count', 'friends_count',
                    'listed_count', 'favourites_count', 'verified', 'statuses_count',
                    'created_at', 'geo_enabled']
            for k in keys:
                pu[k] = getattr(d, k)
                        
            try:
                location = unidecode(d.location.lower().strip())
                pu['location'] = location
            except:
                location = None
                
            try:
                profile_location = unidecode(d.profile_location.lower().strip())
                pu['profile_location'] = profile_location
            except:
                profile_location = None
            
            try:
                L = d.coordinates.coordinates
                lat, lon = L[0], L[1]
            except:
                lat, lon = None, None
            
            if lat and lon:
                LatLon = (str(lat) + str(lon)).replace(".","")
                hashLatLon = hashlib.md5(LatLon.encode()).hexdigest()
                data = tau.checkLatLon(dbParG, hashLatLon, key='locID')
                if data:
                    address = data['address']
                    location = data['location']
                    exist = True
                else:
                    try:
                        gmaps = googlemaps.Client(key=gKey)
                        address = tau.reverseGeo(gmaps, lat, lon, lan='id')
                        del gmaps
                        location = address
                    except:
                        address = None
                    if location:
                        exist = True
            else:
                if location:
                    hashLocation = hashlib.md5(location.encode()).hexdigest()
                    data = tau.checkLatLon(dbParG, hashLocation, key='hash_location')
                    if data:
                        address, lat, lon = data['address'], data['lat'], data['lon']
                        exist = True
                
            gmaps = googlemaps.Client(key=gKey)
            lat, lon, address = tau.getPlace(gmaps, location, lan='id')
            del gmaps
                
            if address:
                p = {'location':location, 'address':address, 'lat':lat, 'lon':lon}
                p = tau.sqlSafe(p)
                qry = tau.qryGcache(p, dbParG)
                tau.insertSQL(dbParG, qry, maxTry=3)
                p = {'location':location, 'address':address, 'lat':lat, 'lon':lon, 'name':pu['name'], 'id_str':pu['id_str'], 'screen_name':pu['screen_name']}
                p = tau.sqlSafe(p)
                qry = tau.qryUpdate(dbParT, p, key = 'screen_name')
                tau.execSQL(dbParT, qry, maxTry=3)
            else:
                try:
                    gmaps = googlemaps.Client(key=gKey)
                    lat, lon, address = tau.getPlace(gmaps, profile_location, lan='id')
                    del gmaps
                except:
                    pass
                if address:
                    p = {'location':location, 'address':address, 'lat':lat, 'lon':lon}
                    p = tau.sqlSafe(p)
                    qry = tau.qryGcache(p, dbParG)
                    tau.insertSQL(dbParG, qry, maxTry=3)
                    p = {'location':location, 'address':address, 'lat':lat, 'lon':lon, 'name':pu['name'], 'id_str':pu['id_str'], 'screen_name':pu['screen_name']}
                    p = tau.sqlSafe(p)
                    qry = tau.qryUpdate(dbParT, p, key = 'screen_name')
                    tau.insertSQL(dbParT, qry, maxTry=3)
                else:
                    try:
                        p = {'location':location} # insert to gcache Lat, lon, lokasi = NULL, tapi area dan hashArea tidak Null
                    except:
                        p = {'location':'-'}
                    p = tau.sqlSafe(p)
                    qry = tau.qryGcache(p, dbParG)
                    try:
                        tau.insertSQL(dbParG, qry, maxTry=3)
                    except:
                        pass
                    p = {'location':location, 'name':name, 'id_str':pu['id_str'], 'screen_name':screen_name}
                    p = tau.sqlSafe(p)
                    qry = tau.qryUpdate(dbParT, p, key = 'screen_name')
                    tau.insertSQL(dbParT, qry, maxTry=3)
            
            p = {'location':location, 'address':address, 'lat':lat, 'lon':lon}
            for key in ['lat', 'lon', 'location', 'address']:
                try:
                    pu[key] = p[key]
                except:
                    pass
            pu['created_at'] = d.created_at.strftime('%Y-%m-%d')
            print('Found these information about the user:\n',pu)
            pu = tau.sqlSafe(pu)
            qry = tau.qryUpdate(dbParU, pu, key = 'screen_name')
            tau.execSQL(dbParU, qry, maxTry=3)
            
            if location:
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
            print("Seems like we're finished :) wait = ", idle+1,'x')
            idle += 1; time.sleep(np.random.randint(nSleepA, nSleepB))
        tau.getTokens(dbParTok, machine_id, status=0) #update status to 0
        time.sleep(30)
        Ck, Cs, At, As = tau.getTokens(dbParTok, machine_id, status=1) #getToken, update status
    tau.getTokens(dbParTok, machine_id, status=0) #update status to 0