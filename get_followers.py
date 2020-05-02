# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 00:23:50 2020
@author: Taufik Sutanto
"""
import tweepy, time, pymysql as pyOld
import taudata_crawl_tweet as tau#, twython
from unidecode import unidecode
from tqdm import tqdm
from twython import Twython#, TwythonRateLimitError

def twython_connect(Ck, Cs, At, As):
    try:
        #twitter = Twython(Ck, Cs, At, As)
        #user = twitter.verify_credentials()
        #print('Welcome "%s" you are now connected to twitter server' %user['name'])
        #return twitter
        return Twython(Ck, Cs, At, As)
    except:
        print("Connection failed, please check your API keys or connection")

def followers(screen_name, id_usr, dbParF, Ck, Cs, At, As):
    """Retrieves all the friends or followers for a given user_id."""
    twitter = twython_connect(Ck, Cs, At, As)
    get_links_ids = twitter.get_followers_ids
    c = 1
    print('Query: '.format(c), end = '')
    next_cursor = -1
    while next_cursor != 0:
        next_links = get_links_ids(user_id=screen_name, cursor=next_cursor, count = 5000)
        next_cursor = next_links['next_cursor']
        print('{}:{}, '.format(c, len(next_links['ids'])), end = ''); c += 1
        qry = 'INSERT INTO {} (screen_name, followee, follower) VALUES '.format(dbParF['tbl'])
        val = []
        for f in next_links['ids']:
            val.append((screen_name, id_usr, f))
        val = str(val)[1:-1]
        qry = qry + val + ' ON DUPLICATE KEY UPDATE screen_name=VALUES(screen_name), followee=VALUES(followee), follower=VALUES(follower)'
        tau.execSQL(dbParF, qry, maxTry=3)
        if next_cursor != 0:
            time.sleep(60)
    return True

def get_followers(dbParF, screen_name, id_usr, Ck, Cs, At, As):
    """
    """
    dbParU = {'db_': 'u8494347_twitter', 'tbl':'twitter_users', 'usr':'u8494347_taufikedys', 'pas':'ppim_UIN_Jakarta', 'hst':'data-university.com'}
    twitter = tau.twitter_connect(Ck, Cs, At, As)
    count = 1
    for page in tweepy.Cursor(twitter.followers, screen_name=screen_name, wait_on_rate_limit=True, count=200).pages():
        print('Query #{} '.format(count))
        count += 1 # break
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
            
            keys = ['location', 'name', 'description', 'followers_count', 'friends_count', 'geo_enabled',
                        'listed_count', 'favourites_count', 'verified', 'statuses_count','id_str','screen_name']
            qry = 'INSERT INTO {} ('.format(dbParU['tbl'])
            qry = qry + ', '.join(keys) + ') VALUES '
            
            val = []
            for d in page:
                D = [getattr(d, k) for k in keys]
                for i, e in enumerate(D):
                    if isinstance(e, str):
                        e = unidecode(e).strip()
                        if e:
                            D[i] = pyOld.escape_string(e)
                        else:
                            D[i] = '-'
                    else:
                        D[i] = e
                val.append(tuple(D))
            val = str(val)[1:-1]
            qry = qry + val + ' ON DUPLICATE KEY UPDATE screen_name=VALUES(screen_name)'
            tau.execSQL(dbParU, qry, maxTry=3)
            
        except tweepy.TweepError as e:
            print("I have to sleep for a minute ZZzzZzZZzzzz...", e)
            for i in tqdm(range(60)):
                time.sleep(1)
    return True