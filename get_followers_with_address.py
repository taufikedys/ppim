# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 00:23:50 2020

@author: Taufik Sutanto
"""
import tweepy, hashlib, googlemaps, time
import taudata_crawl_tweet as tau
from unidecode import unidecode
from tqdm import tqdm

def get_followers(dbParF, screen_name, id_usr, Ck, Cs, At, As):
    """
    get a list of all followers of a twitter account
    :param user_name: twitter username without '@' symbol
    :return: list of usernames without '@' symbol
    """
    gKey = 'AIzaSyBjW1wJtX8ca_KrpzIvL8mWZJcsEBU-fZY'
    dbParG = {'db_': 'u8494347_twitter', 'tbl':'gcache', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParT = {'db_': 'u8494347_twitter', 'tbl':'islam_id_2009_2019', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}

    twitter = tau.twitter_connect(Ck, Cs, At, As)
    count = 1
    for page in tweepy.Cursor(twitter.followers, screen_name=screen_name, wait_on_rate_limit=True, count=200).pages():
        print('Query #{} '.format(count))
        count += 1
        #break
        try:
            followers = [int(p.id) for p in page]
            print('inserting {} followers information to the database'.format(len(followers)))
            qry = 'INSERT INTO {} (screen_name, followee, follower) VALUES '.format(dbParF['tbl'])
            val = []
            for f in followers:
                val.append((screen_name, id_usr, f))
            val = str(val)[1:-1]
            qry = qry + val + ' ON DUPLICATE KEY UPDATE screen_name=VALUES(screen_name), followee=VALUES(followee), follower=VALUES(follower)'
            tau.execSQL(dbParF, qry, maxTry=3)
            # Sayang informasi lain dari follower kalau ndak disimpan ... saving ke Table twitter users
            for d in page:
                adaU = tau.checkExist(dbParU, 'screen_name', d.screen_name, maxTry=1)
                #break
                if not adaU:
                    existG, address, location, lat, lon = False, None, None, None, None
                        
                    try:
                        location = unidecode(d.profile_location +' '+ d.location).lower().strip()
                    except:
                        location = unidecode(d.location).lower().strip()
                    if not location:
                        try:
                            location = unidecode(d.description).lower().strip()
                        except:
                            pass
                        
                    try:
                        lat, lon = d.coordinates.coordinates[0], d.coordinates.coordinates[1]
                    except:
                        pass
                    
                    if lat and lon:
                        LatLon = (str(lat) + str(lon)).replace(".","")
                        hashLatLon = hashlib.md5(LatLon.encode()).hexdigest()
                        data = tau.checkLatLon(dbParG, hashLatLon, key='locID', maxTry=1)
                        if data:
                            address = data['address']
                            location = data['location']
                            existG = True
                        else:
                            try:
                                gmaps = googlemaps.Client(key=gKey)
                                address = tau.reverseGeo(gmaps, lat, lon, lan='id')
                                del gmaps
                                location = address
                            except:
                                address = None
                    else:
                        if location:
                            hashLocation = hashlib.md5(location.encode()).hexdigest()
                            data = tau.checkLatLon(dbParG, hashLocation, key='hash_location', maxTry=1)
                            if data:
                                address, lat, lon = data['address'], data['lat'], data['lon']
                                existG = True
                                
                    if location and not address and not lat:
                        gmaps = googlemaps.Client(key=gKey)
                        lat, lon, address = tau.getPlace(gmaps, location, lan='id')
                        del gmaps
                        
                    # location, address, lat, lon
                    if not existG and location and address and lat:
                        p = {'location':location, 'address':address, 'lat':lat, 'lon':lon}
                        p = tau.sqlSafe(p)
                        qry = tau.qryGcache(p, dbParG)
                        tau.insertSQL(dbParG, qry, maxTry=3)
                    else:
                        location = '--'
                    
                    pu = {'location':location, 'address':address, 'lat':lat, 'lon':lon, 'name':d.name, 'id_str':d.id_str, 'screen_name':d.screen_name}
                    qry = tau.qryUpdate(dbParT, tau.sqlSafe(pu), key = 'screen_name')
                    tau.execSQL(dbParT, qry, maxTry=3)
                    
                    keys = ['description', 'followers_count', 'friends_count', 'geo_enabled',
                            'listed_count', 'favourites_count', 'verified', 'statuses_count']
                    for k in keys:
                        pu[k] = getattr(d, k)
                    
                    pu['created_at'] = d.created_at.strftime('%Y-%m-%d')
                    print('Inserting detail information about:',d.screen_name)
                    qry = tau.qryInsert(tau.sqlSafe(pu), dbParU)
                    tau.execSQL(dbParU, qry, maxTry=3)
            
        except tweepy.TweepError as e:
            print("I have to sleep for a minute ZZzzZzZZzzzz...", e)
            for i in tqdm(range(60)):
                time.sleep(1)
    return True