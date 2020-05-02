# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:25:43 2019
@author: Taufik Sutanto
taufik@tau-data.id
https://tau-data.id
TO DO:
* Use COLORAMA untuk mewarnai text di terminal window
* Location update in Batch cari semua yg sama ==> update semua sekaligus
* Followers info pakai "Count" jadi bisa resume juga
"""
import warnings; warnings.simplefilter('ignore')
import time, pymysql as pyOld, mysql.connector as pymysql
import hashlib, re, tweepy, sys, pandas as pd, pickle
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from datetime import datetime
from unidecode import unidecode
from urllib.parse import quote#, unquote
import taudata as tau2
from sklearn.datasets import fetch_20newsgroups
from nltk.corpus import brown
from sklearn.feature_extraction.text import CountVectorizer

def enCorpus(lan = 'en'):
    print('Loading some corpus: ', end='')
    if lan.lower().strip() in ['en', 'english', 'inggris', 'eng']:
        print('English Stopwords,  ', end='')
        corpus = tau2.LoadStopWords(lang='en')[0] #set
        print('News20, ', end='')
        try:
            f = open('data/20newsgroups.pckl', 'rb')
            news = pickle.load(f); f.close()
        except:
            categories = ['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc', 'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware',
             'comp.windows.x', 'misc.forsale', 'rec.autos', 'rec.motorcycles', 'rec.sport.baseball', 'rec.sport.hockey',
             'sci.crypt', 'sci.electronics', 'sci.med', 'sci.space', 'soc.religion.christian', 'talk.politics.guns',
             'talk.politics.mideast', 'talk.politics.misc', 'talk.religion.misc']
            data = fetch_20newsgroups(categories=categories,remove=('headers', 'footers', 'quotes'))
            news = [doc for doc in data.data]
            for i, r in enumerate(news):
                news[i] = tau2.cleanText(r, symbols_remove = True, min_charLen = 3, max_charLen = 12, fixTag= True, fixMix=True)
            f = open('data/tdm2Apr.pckl', 'wb')
            pickle.dump(news, f); f.close()
        
        binary_vectorizer = CountVectorizer(binary = True)
        _ = binary_vectorizer.fit_transform(news)
        newsCorpus = set([v for v,k in binary_vectorizer.vocabulary_.items()])
        corpus.update(newsCorpus)
        print('NLTK Brown Corpus')
        Brown = set([str(t).lower().strip() for t in brown.words()])
        corpus.update(Brown)
    elif lan.lower().strip() in ['id', 'indonesia', 'indonesian']:
        print('Stopwords Bahasa,  ', end='', flush = True)
        corpus = tau2.LoadStopWords(lang='id')[0] #set
        print('kata dasar,  ', end='', flush = True)
        corpus.update(set(tau2.loadPos_id(file = 'data/kata_dasar.txt')))
        print('lexicons,  ', end='', flush = True)
        corpus.update(set([t.strip() for t in tau2.LoadDocuments(file = 'data/kataPosID.txt')[0]]))
        corpus.update(set([t.strip() for t in tau2.LoadDocuments(file = 'data/kataNegID.txt')[0]]))
        print('Fixed slang,  ', end='', flush = True)
        cc = tau2.loadPos_id(file = 'data/slang.dic')
        cc = [t.strip().lower() for t in cc.values() if len(t)>2]
        corpus.update(set(cc))
        print('tags.', flush = True)
        cc = tau2.loadPos_id(file = 'data/Indonesian_Manually_Tagged_Corpus.tsv')
        cc = [t.strip().lower() for t in cc.keys() if len(t)>2]
        corpus.update(set(cc))
    else:
        sys.exit('Language not supported')
    print('Cleanups ... ')
    C = [k.lower().strip() for k in corpus if len(k)>2]
    return set(C)

def getLocations(dbParT, maxTry=3):
    try_, qry = 0, "SELECT distinct(LOWER(location)) FROM {} WHERE location IS NOT NULL".format(dbParT['tbl'])
    # "SELECT location, address, lat, lon FROM {} WHERE address IS NOT NULL".format(dbParG['tbl'])
    while try_<maxTry:
        try:
            db = conMql(dbParT); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                return data
            else:
                return None
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)
    return None
    
def pyPriority():
    """ Set the priority of the process to High."""
    import sys
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        import win32api,win32process,win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    else:
        import os
        os.nice(10)

def generateTimes(year_start=2009, year_end = 2019):
    waktu = []
    years = list(map(str,range(year_start, year_end+1)))
    months = list(map(str,range(1, 10)))
    months = ['0'+m for m in months] + ['11', '12']
    for y in years:
        for m in months:
            w = '-'.join([y, m, '01'])
            waktu.append(w)
    return waktu

def loadQry(fQry, waktu, language=None):
    """
        Query format di txt: 
            allWords: islam quran; frase: ahli sunah, puasa ramadhan; anyWords: akhlak akhlaq; filter: babi anjing
        
        url = 'https://twitter.com/search?l=id&q=islam%20quran%20%22puasa%20sunah%22%20hadist%20OR%20akhlaq%20-babi%20-anjing%20from%3Aaagym%20since%3A2019-06-05%20until%3A2020-01-13&src=typd'
        from urllib.parse import unquote
        print(unquote(url))
        
        url = 'https://twitter.com/search?l=id&q=islam quran "puasa sunah" hadist OR akhlaq -babi -anjing from:aagym since:2019-06-05 until:2020-01-13&src=typd'
        
        from urllib.parse import quote
        quote(url)
    """
    if '.txt' in fQry[-4:]:
        file = open(fQry, 'r', encoding="utf-8", errors='replace')
        F = file.readlines()
        file.close()
        return [f.strip().lower() for f in F]
    elif '.csv' in fQry[-4:]:
        Q = pd.read_csv(fQry, error_bad_lines=False, low_memory = False)
        Queries = [] # 
        keys = ['allwords', 'frase', 'anywords', 'filter']
        for i, q in Q.iterrows():
            tmp = []
            if language:
                qry = 'https://twitter.com/search?l='+language+'&q='
            else:
                qry = 'https://twitter.com/search?&q='
            for k in keys:    
                if isinstance(q[k], str) and q[k].strip():
                    q[k] = q[k].lower().strip()
                    if ',' in q[k]:
                        if k =='allwords':
                            # allwords SEHARUSNYA tidak memiliki ","
                            tmp.append(q[k].replace(',',' OR '))
                        elif k=='frase':
                            t_ = ['"'+f.strip()+'"' for f in q[k].split(',')]
                            tmp.append(' OR '.join(t_))
                        elif k=='anywords':
                            t_ = [f.strip() for f in q[k].split(',')]
                            tmp.append(' OR '.join(t_))
                        elif k=='filter':
                            t_ = ['-'+f.strip() for f in q[k].split(',')]
                            tmp.append(' '.join(t_))
                    else:
                        if k =='allwords':
                            tmp.append(q[k])
                        elif k=='frase':
                            tmp.append('"'+q[k]+'"')
                        elif k=='anywords':
                            tmp.append(' OR ' + q[k])
                        elif k=='filter':
                            tmp.append('-'+q[k])
            qry += quote(' '.join(tmp))
            for t, wkt in enumerate(waktu):
                try:
                    Queries.append(qry + '%20since%3A{}%20until%3A{}&src=typd'.format(wkt, waktu[t+1]))
                except:
                    pass
        return Queries
    else:
        sys.exit('Unknown query file format, please use either txt or csv file only')

def cekExistR(Q, dbG, maxTry=3):
    """
    Query is exist di dbParG
    """
    try_, qry = 0, "SELECT * FROM {} WHERE hashQry = '{}' LIMIT 1".format(dbG['tbl'], Q)
    while try_<maxTry:
        try:
            db = pymysql.connect(host=dbG['hst'], user=dbG['usr'], passwd=dbG['pas'], db=dbG['db_'])
            cur = db.cursor();cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                try:
                    qry = 'INSERT INTO {} (hashQry) VALUES ("{}")'.format(dbG['tbl'], Q)
                    db = conMql(dbG)# pymysql.connect(host=dbParR['hst'], user=dbParR['usr'], passwd=dbParR['pas'], db=dbParR['db_'])
                    cur = db.cursor(); cur.execute(qry)
                    db.close();cur.close()
                    return True
                except:
                    try_ += 1; time.sleep(1)
            else:
                return False
        except:
            try_ += 1; time.sleep(1)
    return False

def convSqlTime(wkt):
    # time='29,06,2012', tSQl = '2012-06-29'
    bln = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 
           'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    tSql = wkt.split(',')[::-1]
    if len(tSql)==1:
        tSql = wkt.split(' ')[::-1]
    if len(tSql[0])==2:
        tSql[0] = '20'+tSql[0]
    tSql[1] = bln[tSql[1]]
    tSql = '-'.join(tSql)
    return tSql

def getQry(machineID, dbParQ, maxTry=3): 
    # get uRl, update machineID, TImeStamp, dan status to 1
    try_, qry = 0, "SELECT id_, qry, hashQry FROM {} WHERE status = 0 LIMIT 1".format(dbParQ['tbl'])
    while try_<maxTry:
        try:
            db = conMql(dbParQ)
            cur = db.cursor();cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                id_, qry, hashQry = data[0]
                try:
                    q = 'UPDATE {} SET status = 1, machine_id = {} WHERE hashQry ="{}"'.format(dbParQ['tbl'], machineID, hashQry)
                    db = conMql(dbParQ)# pymysql.connect(host=dbParR['hst'], user=dbParR['usr'], passwd=dbParR['pas'], db=dbParR['db_'])
                    cur = db.cursor(); cur.execute(q)
                    db.close();cur.close()
                    return id_, qry, hashQry
                except:
                    try_ += 1; time.sleep(1)
            else:
                return None, None, None
        except:
            try_ += 1; time.sleep(1)    
    return None, None, None

def updateQry(hashQry, dbParQ, maxTry=3): 
    try_, qry = 0, 'UPDATE {} SET status = 2 WHERE hashQry ="{}"'.format(dbParQ['tbl'], hashQry)
    while try_<maxTry:
        try:
            db = conMql(dbParQ)
            cur = db.cursor();cur.execute(qry)
            cur.fetchall()
            cur.close();db.close()
            return True
        except:
            try_ += 1; time.sleep(1)    
    return False


def getTweets(url, lan=None, headers=None):
    urlPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    if not headers:
        headers = {'User-Agent' : "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    
    start = url.find('%20since%3A')+len('%20since%3A')
    end = url.find('%20until%3A')
    default_time = url[start:end]
    
    req = Request(url, headers = headers)
    resp = urlopen(req).read()
    soup = bs(resp,'html.parser')
    Tweets = soup.find_all(class_= 'tweet')
    posts = []
    for t in Tweets:        
        screen_name = t.find_all(class_= 'username')[0]
        screen_name = unidecode(bs(str(screen_name),'html.parser').text.replace('@','').strip())
        
        created_at = t.find_all(class_= 'timestamp')[0]
        created_at = bs(str(created_at),'html.parser').text.strip()
        try:
            created_at = convSqlTime(created_at)
        except:
            created_at = default_time
            
        try:
            propic = t.find_all(class_= 'avatar')[0]
            propic = propic.findAll('img')[0]
            propic = unidecode(re.findall(urlPattern,str(propic))[0])
            #propic = pyOld.escape_string(propic)
        except:
            propic = None
        
        try:
            name = t.find_all(class_= 'fullname')[0]
            name = unidecode(bs(str(name), "lxml").text)
            #name = pyOld.escape_string(name)
        except:
            name = None
        
        id_str = None
        
        try:
            areplyto = t.find_all(class_= 'tweet-reply-context username')[0]
            areplyto = areplyto.find_all('a')[0]
            areplyto = unidecode(bs(str(areplyto), "lxml").text.replace('@',''))
            #areplyto = pyOld.escape_string(areplyto)
        except:
            areplyto = None
        
        tweet = t.find_all(class_= 'tweet-text')[0]
        tweet = unidecode(bs(str(tweet),'html.parser').text.strip())
        #tweet = pyOld.escape_string(tweet)
        
        if 'rt @' in tweet[:5].lower() or ' RT ' in tweet:
            isRetweet = 1
        else:
            isRetweet = 0
            
        url_tweet = str(t).split('\n')[0]
        mulai, akhir = url_tweet.find('href="/')+len('href="/'), url_tweet.find('">')
        url_tweet = 'https://twitter.com/' + url_tweet[mulai:akhir]
        #url_tweet = pyOld.escape_string(url_tweet)
        
        tweetID = hashlib.md5(url_tweet.encode()).hexdigest()
        
        if not lan:
            lan = None
        
        key = ['tweetID', 'created_at', 'screen_name', 'id_str', 'tweet', 'areplyto', 'name', 'language', 'url', 'propic']
        val = [tweetID, created_at, screen_name, id_str, tweet, areplyto, name, lan, url_tweet, propic]
        data = {k:v for k,v in zip(key,val) if v}
        data['isretweet'] = isRetweet
        posts.append(data)

    try:
        nextPage = soup.find_all(class_= 'w-button-more')[0]
        nextPage = str(nextPage).split('\n')[1]
        mulai, akhir = nextPage.find('href="/')+len('href="/'), nextPage.find('">')
        nextPage = 'https://twitter.com/' + nextPage[mulai:akhir]            
    except:
        nextPage = None
            
    return posts, nextPage

#@timeout_decorator.timeout(30)
def insertTweet(posts, dbParT, maxTry=3):
    """
    """
    print('\ninserting {} posts to the database'.format(len(posts)))
    keys = set()
    for p in posts:
        keys.update(set(p.keys()))
    keys = list(keys)
    qry = 'INSERT INTO {} ('.format(dbParT['tbl'])
    qry = qry + ', '.join(keys) + ') VALUES '
    val = []
    for d in posts:
        D = []
        for k in keys:
            if k in d.keys():
                if isinstance(d[k], str):
                    tmp_ = pyOld.escape_string( unidecode(d[k]).strip() )
                    D.append(tmp_)
                else:
                    D.append(d[k])
            else:
                D.append('')
        val.append(tuple(D))
    qry = qry + str(val)[1:-1] + ' ON DUPLICATE KEY UPDATE tweetID=VALUES(tweetID)'
    try_ = 0
    while try_<maxTry:
        try:
            db = conMql(dbParT); cur = db.cursor()
            cur.execute(qry)
            cur.close();db.close()
            return True
            try_ = maxTry + 1
        except:
            if try_ == 0:
                print('query Error =\n{}'.format(qry))
                qry = "INSERT INTO error_log ( error ) VALUES ( %s );" %('"query Error =\n{}"'.format(qry))
                db = conMql(dbParT); cur = db.cursor()
                cur.execute(qry)
                cur.close();db.close()
            try_ += 1; time.sleep(1)
    return False
    
#@timeout_decorator.timeout(10)
def getTweetInfo(dbParT, limit = 3, idx=-1, maxTry=3):    
    try_, qry = 0, "SELECT tweetID, url, screen_name, created_at FROM {} WHERE nretweets IS NULL LIMIT {}".format(dbParT['tbl'], limit)
    while try_<maxTry:
        try:
            db = conMql(dbParT); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                return data[idx]
            else:
                return None
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)

#@timeout_decorator.timeout(10)
def getNoAreaUsr(dbParT, maxTry=3):
    try_, qry = 0, "SELECT tweetID, url, screen_name, id_str, name FROM {} WHERE address IS NULL LIMIT 1".format(dbParT['tbl'])
    while try_<maxTry:
        try:
            db = conMql(dbParT); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                p = {'address':'--', 'screen_name':data[0][2]}
                qry = qryUpdate(dbParT, p, key = 'screen_name')
                db = conMql(dbParT); cur = db.cursor()
                cur.execute(qry)
                cur.close();db.close()
                return data[0]
            else:
                return None
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)
    return None

def getUsrDetails(screen_name, Ck,Cs,At,As, dbParTok, machine_id, maxTry = 3):
    # getUsrDetails(screen_name, Ck,Cs,At,As, dbParTok, machine_id,maxTry = 3)
    try_ = 0
    while try_<maxTry:
        try:
            twitter = twitter_connect(Ck, Cs, At, As)
            d = twitter.get_user(screen_name=screen_name)
            del twitter
            try_ = maxTry + 1
            return d
        except tweepy.TweepError as e:
            print(e)
            return None
        except:
            try_ += 1
            print('retrying ... ')
            getTokens(dbParTok, machine_id, key = At, status=0)
            Ck, Cs, At, As = getTokens(dbParTok, machine_id, key = None, status=1) 
    return None


def getTokens(dbParTok, machine_id, status=1, key = None, maxTry=3):
    try_ = 0
    qry = "SELECT customer_token,customer_secret, access_token,access_secret FROM {} ORDER BY timestamp LIMIT 1".format(dbParTok['tbl'])
    while try_<maxTry:
        try:
            db = conMql(dbParTok); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                if key:
                    qry = 'UPDATE {} SET status = {}, machine_id ="{}" WHERE access_token="{}"'.format(dbParTok['tbl'], status, machine_id, key)
                else:
                    qry = 'UPDATE {} SET status = {}, machine_id ="{}" WHERE access_token="{}"'.format(dbParTok['tbl'], status, machine_id, data[0][2])
                execSQL(dbParTok, qry, maxTry=3) # update status to 1: "in use"
                try:
                    return data[0]
                except:
                    return None
            else:
                return None
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)
    return None

def checkLatLon(dbParG, hashVal, key='', maxTry=3):
    try_, qry = 0, "SELECT lat, lon, location, address FROM {} WHERE {}='{}' LIMIT 1".format(dbParG['tbl'], key, hashVal)
    while try_<maxTry:
        try:
            db = conMql(dbParG); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                data = data[0]
                return {'lat':data[0], 'lon':data[1], 'location':data[2], 'address':data[3]}
            else:
                return None
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)
    return None

def getUsrFollow(dbParT, dbParF, key='', limit=1, idx=0, maxTry=3):
    #qry = "SELECT screen_name, id_str FROM {} WHERE {} NOT IN (SELECT {} FROM {}) LIMIT {}".format(dbParU['tbl'], key, key, dbParF['tbl'], limit)
    qry = 'SELECT screen_name, id_str FROM {} WHERE {} NOT IN (SELECT DISTINCT({}) FROM {}) ORDER BY nretweets DESC LIMIT {}'.format(dbParT['tbl'], key, key, dbParF['tbl'], limit)
    try_ = 0
    while try_<maxTry:
        try:
            db = conMql(dbParT); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                return data[idx]
            else:
                return None
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)
    return None

def getidusr(screen_name, dbParU, dbParT, Ck, Cs, At, As, dbParTok, machine_id):
    # getidusr(screen_name, dbParU, dbParT, Ck, Cs, At, As, dbParTok, machine_id)
    # get id_usr and all other information, update di twitter table and user table
    # getUsrDetails(screen_name, Ck,Cs,At,As, dbParTok, machine_id, maxTry = 3)
    d = getUsrDetails(screen_name, Ck,Cs,At,As, dbParTok, machine_id,maxTry = 3)
    if d:
        pu = {}
        keys = ['name', 'description', 'id_str', 'followers_count', 'friends_count',
                        'listed_count', 'favourites_count', 'verified', 'statuses_count',
                        'created_at', 'geo_enabled', 'screen_name']
        for k in keys:
            pu[k] = getattr(d, k)
        try:
            location = unidecode(d.location.lower().strip())
            pu['location'] = location
        except:
            location = None
        try:
            pu['location'] = pu['profile_location'] +' '+ unidecode(d.profile_location.lower().strip())
        except:
            pass
        try:
            lat, lon = d.coordinates.coordinates[0], d.coordinates.coordinates[1]
        except:
            lat, lon = None, None
            
        pu['created_at'] = d.created_at.strftime('%Y-%m-%d')
        print('Found these information about the user:\n',pu)
        pu = sqlSafe(pu)
        qry = qryUpdate(dbParU, pu, key = 'screen_name')
        execSQL(dbParU, qry, maxTry=3)
        
        # Update Table Tweets
        keys = ['id_str', 'location', 'screen_name', 'name']
        p = {k:getattr(d, k) for k in keys}
        p['lat'], p['lon'] = lat, lon
        p = sqlSafe(p)
        qry = qryUpdate(dbParT, p, key = 'screen_name')
        execSQL(dbParT, qry, maxTry=3)
        return d.id
    else:
        return None

def getTweetsStat(url, date, headers = None):
    """
    """
    #if not headers:
    #    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        #headers = {'User-Agent' : "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    try:
        #req = Request(url, headers = headers)
        req = Request(url)
        resp = urlopen(req).read()
        soup = bs(resp,'html.parser')
        t = soup.find_all(class_= 'tweet')[0]
        
        time_url = str(t.find_all(class_= 'tweet-timestamp')[0])
        mulai = time_url.find('data-time-ms="')+len('data-time-ms="')
        akhir = mulai + time_url[mulai:].find('">')
        try:
            wkt = int(time_url[mulai:akhir])
            wkt = datetime.fromtimestamp(wkt/1000.0)
            wkt = wkt.strftime('%Y-%m-%d') # ('%Y-%m-%d %H:%M:%S')
        except:
            wkt = date
            
        try:
            nReplies = t.find_all(class_= 'ProfileTweet-action--reply')[0] # 
            nReplies = bs(str(nReplies),'html.parser').text.strip()
            nReplies = int(''.join([d for d in nReplies if d.isdigit()]))
        except:
            nReplies = 0
            
        try:
            nRetweet = t.find_all(class_= 'ProfileTweet-action--retweet')[0] # 
            nRetweet = bs(str(nRetweet),'html.parser').text.strip()
            nRetweet = int(''.join([d for d in nRetweet if d.isdigit()]))
        except:
            nRetweet = 0
            
        try:
            nLikes = t.find_all(class_= 'ProfileTweet-action--favorite')[0] # 
            nLikes = bs(str(nLikes),'html.parser').text.strip()
            nLikes = int(''.join([d for d in nLikes if d.isdigit()]))
        except:
            nLikes = 0
            
        key = ['created_at', 'nretweets', 'nreplies', 'nlikes']
        val = [wkt, nRetweet, nReplies, nLikes]
        return {k:v for k,v in zip(key,val)}
    except:
        return None

#@timeout_decorator.timeout(10)
def updateTweet(p, dbParT, maxTry = 3):
    try_ = 0
    while try_<maxTry:
        try:
            qry_0 = "UPDATE {} SET ".format(dbParT['tbl'])
            val = []
            for k,v in p.items():
                if k!='tweetID':
                    if isinstance(v, str):
                        val.append(str(k)+"='"+v+"'")
                    else:
                        val.append(str(k)+"="+str(v))
            qry_1 = " WHERE tweetID = '{}'".format(p['tweetID'])
            qry = qry_0 + ', '.join(val)+ qry_1
            
            db = conMql(dbParT); cur = db.cursor()
            cur.execute(qry)
            cur.close();db.close()
            try_ = maxTry + 1
            return True
        except:      
            print("Error updating tweetID = ", p['tweetID'], ' try = ', try_)
            try_ += 1; time.sleep(1)
    return False


def conMql(dbPar, maxTry = 3):
    try_ = 0
    while try_<maxTry:
        try:
            return pymysql.connect(host=dbPar['hst'],user=dbPar['usr'],passwd=dbPar['pas'],db=dbPar['db_'])
        except (pymysql.Error) as e:      
            print ("Error Connecting to MySQL %d: %s" % (e.args[0],e.args[1]))
            try_ += 1; time.sleep(1)

#@timeout_decorator.timeout(10)
def getPlace(gmaps, place, lan='id'):
    try:
        res = gmaps.geocode(place, language=lan)[0]
    except:
        return None, None, None
    if res:
        lat, lon = res['geometry']['location']['lat'], res['geometry']['location']['lng']
    addresses = res['address_components']
    alamat = [a['long_name'] for a in addresses]
    return lat, lon, ' '.join(alamat)

#@timeout_decorator.timeout(10)
def reverseGeo(gmaps, lat, lon, lan='id'):
    try:# lat, lon = -6.404952, 106.817276
        res = gmaps.reverse_geocode((lat, lon), language=lan)[0]
        return res['formatted_address']
    except:
        return None

#@timeout_decorator.timeout(10)
def getHeaders():
    """
    do NOT rotate header if proxy is not rotated
    
    """
    headers = {}
    try:
        import shadow_useragent 
        ua = shadow_useragent.ShadowUserAgent()
        ua = ua.get_sorted_uas()[0]['useragent']
    except:
        ua = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    headers['User-Agent'] = ua
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    #headers['referrer'] = 'https://www.google.com'
    return headers

#@timeout_decorator.timeout(30)
def twitter_connect(Ck, Cs, At, As):
    try:
        auth = tweepy.OAuthHandler(Ck, Cs)
        auth.set_access_token(At, As)
        twitter = tweepy.API(auth, timeout=600)
        #user = twitter.verify_credentials()
        #print('Welcome "%s" you are now connected to twitter server' %user.name)
        return twitter
    except:
        print("Connection failed, please check your API keys or connection")
        return None

def qryGcache(p, dbG):
    location = unidecode(p['location'].lower().strip())
    hash_location = hashlib.md5(location.encode()).hexdigest()
    if 'lat' in p.keys():
        lat, lon, address = p['lat'], p['lon'], p['address']
        locID = (str(lat) + str(lon)).replace(".","")
        locID = hashlib.md5(locID.encode()).hexdigest()
        
        return 'INSERT INTO {} (lat, lon, location, address, hash_location, locID) VALUES ({},{},"{}","{}","{}","{}")'.\
            format(dbG['tbl'], lat, lon, pyOld.escape_string(location), pyOld.escape_string(address), hash_location, locID)
    else:
        return 'INSERT INTO {} (location, hash_location) VALUES ("{}","{}")'.\
            format(dbG['tbl'], pyOld.escape_string(location), hash_location)

def qryInsert(p, dbParT):
    columns = str(tuple(p.keys())).replace("'","")
    qry = "INSERT INTO %s %s VALUES (" % (dbParT['tbl'], columns)
    val = []
    for v in p.values():
        if isinstance(v, str):
            val.append(v)
        else:
            val.append(str(v))
    return qry + ', '.join(val)+ ')'

def qryUpdate(dbPar, p, key = 'screen_name'):
    qry_0 = "UPDATE {} SET ".format(dbPar['tbl'])
    val = []
    for k, v in p.items():
        if k!=key:
            if isinstance(v, str):
                val.append(str(k)+'="'+pyOld.escape_string(unidecode(v))+'"')
            else:
                val.append(str(k)+"="+str(v))
    if isinstance(p[key], str):
        qry_1 = ' WHERE {} = "{}"'.format(key, p[key])
    else:
        qry_1 = " WHERE {} = {}".format(key, p[key])
    return qry_0 + ', '.join(val)+ qry_1

#@timeout_decorator.timeout(30)
def insertSQL(dbG, qry, maxTry=3):
    try_ = 0
    while try_<maxTry:
        try:
            db = conMql(dbG)
            cur = db.cursor(); cur.execute(qry)
            db.close();cur.close()
            return True
        except:
            try_ += 1; time.sleep(3)
    return False

def execSQL(dbG, qry, maxTry=3):
    try_ = 0
    while try_<maxTry:
        try:
            db = conMql(dbG)
            cur = db.cursor()
            res = cur.execute(qry)
            db.close();cur.close()
            return res
        except:
            try_ += 1; time.sleep(3)
    return False

#@timeout_decorator.timeout(10)
def checkExist(dbParG, col, val, maxTry=3):
    try_ = 0
    if isinstance(val, str):
        qry = "SELECT * FROM {} WHERE {}='{}' LIMIT 1".format(dbParG['tbl'], col, val)
    else:
        qry = "SELECT * FROM {} WHERE {}={} LIMIT 1".format(dbParG['tbl'], col, val)
    while try_<maxTry:
        try:
            db = conMql(dbParG); cur = db.cursor()
            cur.execute(qry)
            data = cur.fetchall()
            cur.close();db.close()
            if data:
                return True
            else:
                return False
            try_ = maxTry + 1
        except:
            try_ += 1; time.sleep(1)
    return False

def sqlSafe(entity):
    dic = {}
    for k, v in entity.items():
        if isinstance(v, str):
            V = unidecode(v).strip()
            if V:
                dic[k] = ''.join(['"',pyOld.escape_string(V),'"'])
            else:
                dic[k] = '"--"'
        elif v is None:
            pass
        else:
            dic[k] = v
        if k=='location' and (v=='' or v==None):
            dic[k] = '"--"'
    return dic
        