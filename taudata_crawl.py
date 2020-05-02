# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:25:43 2019
@author: Taufik Sutanto
taufik@tau-data.id
https://tau-data.id

~~Perjanjian Penggunaan Materi & Codes (PPMC) - License:~~
* Modul Python dan gambar-gambar (images) yang digunakan adalah milik dari berbagai sumber sebagaimana yang telah dicantumkan dalam masing-masing license modul, caption atau watermark.
* Materi & Codes diluar point (1) (i.e. "taudata.py" ini & semua slide ".ipynb)) yang digunakan di pelatihan ini dapat digunakan untuk keperluan akademis dan kegiatan non-komersil lainnya.
* Untuk keperluan diluar point (2), maka dibutuhkan izin tertulis dari Taufik Edy Sutanto (selanjutnya disebut sebagai pengarang).
* Materi & Codes tidak boleh dipublikasikan tanpa izin dari pengarang.
* Materi & codes diberikan "as-is", tanpa warranty. Pengarang tidak bertanggung jawab atas penggunaannya diluar kegiatan resmi yang dilaksanakan pengarang.
* Dengan menggunakan materi dan codes ini berarti pengguna telah menyetujui PPMC ini.
"""
import warnings; warnings.simplefilter('ignore')
import pandas as pd, timeout_decorator, sys, seaborn as sns; sns.set()
from tqdm import tqdm
import csv, json, time, pymysql as pyOld
from twython import TwythonStreamer 
import networkx as nx, operator, numpy as np, hashlib #, tika, 
#import pyLDAvis, pyLDAvis.sklearn; pyLDAvis.enable_notebook()
import requests#, googlemaps
#from datetime import datetime
#import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from bs4.element import Comment
from tika import parser#, unpack
from nltk.tokenize import TweetTokenizer; Tokenizer = TweetTokenizer(reduce_len=True)
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.decomposition import LatentDirichletAllocation as LDA
from bz2 import BZ2File as bz2
from scipy import special
from collections import Counter
import re, matplotlib.pyplot as plt, community, os, folium
#from folium import plugins#, spacy
#from spacy.lang.id import Indonesian
from twython import Twython, TwythonRateLimitError
import itertools, nltk
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer;ps = PorterStemmer()
from itertools import chain
from html import unescape
from nltk import sent_tokenize
from unidecode import unidecode
from tqdm import trange #,tqdm
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import urllib.parse
from lxml.html import fromstring
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import mysql.connector as pymysql
from gensim.models.ldamodel import LdaModel
from gensim.models.coherencemodel import CoherenceModel
from math import radians, cos, sin, asin, sqrt
from spacy.lang.id import Indonesian
from nltk.tag import CRFTagger
from datetime import datetime

nlp_id = Indonesian();ct = CRFTagger()  # Language Model
fTagger = 'data/all_indo_man_tag_corpus_model.crf.tagger'
ct.set_model_file(fTagger)

def haversine(lon1=0.0, lat1=0.0, lon2=0.0, lat2=0.0): 
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
    
def NLPfilter(t, filters):
    tokens = nlp_id(t)
    tokens = [str(k) for k in tokens if len(k)>2]
    hasil = ct.tag_sents([tokens])
    return [k[0] for k in hasil[0] if k[1] in filters]

def compute_coherence_values(dictionary, corpus, texts, limit, coherence='c_v', start=2, step=3):
    """
    https://datascienceplus.com/evaluation-of-topic-modeling-topic-coherence/
    Compute c_v coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    model_list = []
    for num_topics in tqdm(range(start, limit, step)):
        model=LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence=coherence)
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values

def generateBaseMap(default_location=[-0.789275, 113.921], default_zoom_start=5):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start)
    return base_map

def saveResume(entry, file=''):
    with open(file, 'a') as f:
        f.write(str(entry)+'\n')

def NextTweets(next_):
    url = urllib.parse.quote(next_.lower().strip())
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    req = Request(url, headers = headers)
    resp = urlopen(req).read()
    soup = bs(resp,'html.parser')
    Tweets = soup.find_all(class_= 'tweet')
    posts = []
    for t in Tweets:
        usr = t.find_all(class_= 'username')[0]
        usr = bs(str(usr),'html.parser').text.replace('@','').strip()
        wkt = t.find_all(class_= 'timestamp')[0]
        wkt = bs(str(wkt),'html.parser').text.strip()
        tweet = t.find_all(class_= 'tweet-text')[0]
        tweet = bs(str(tweet),'html.parser').text.strip()
        url = str(t).split('\n')[0]
        mulai, akhir = url.find('href="/')+len('href="/'), url.find('">')
        url = 'https://twitter.com/' + url[mulai:akhir]
        posts.append({'time':wkt, 'username':usr, 'tweet':tweet, 'link':url, 'lat':'', 'lon':'', 'location':''})
    if posts:
        try:
            nextPage = soup.find_all(class_= 'w-button-more')[0]
            nextPage = str(nextPage).split('\n')[1]
            mulai, akhir = nextPage.find('href="/')+len('href="/'), nextPage.find('">')
            nextPage = 'https://twitter.com/' + nextPage[mulai:akhir]
        except:
            nextPage = None
    else:
        posts = None
    return posts, nextPage

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

def getTweets(url, headers = None): # , loc = '', lat=0.0, lon=0.0
    """
    Filter berdasarkan nama akun atau if "word" in status
    Topic Modelling: tanpa retweet
    Viral : retweet included 
    
    Retweet check : Awal "RT" DAN " RT " in tweet  ==> 0, 1
    """
    urlPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    if not headers:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    posts = []
    req = Request(url, headers = headers)
    resp = urlopen(req).read()
    soup = bs(resp,'html.parser')
    Tweets = soup.find_all(class_= 'tweet')
    for t in Tweets:
        usr = t.find_all(class_= 'username')[0]
        usr = bs(str(usr),'html.parser').text.replace('@','').strip()
        wkt = t.find_all(class_= 'timestamp')[0]
        wkt = bs(str(wkt),'html.parser').text.strip()
        try:
            wkt = convSqlTime(wkt)
        except:
            wkt = datetime.today().strftime('%Y-%m-%d')
        try:
            propic = t.find_all(class_= 'avatar')[0]
            propic = propic.findAll('img')[0]
            propic = re.findall(urlPattern,str(propic))[0]
        except:
            propic = ''
        
        try:
            fullname = t.find_all(class_= 'fullname')[0]
            fullname = bs(str(fullname), "lxml").text
        except:
            fullname = ''
        try:
            usrID = propic.split('/')
            for elemen in usrID:
                try:
                    usrID = int(elemen)
                except:
                    pass
        except:
            usrID = 0
        
        try:
            areplyto = t.find_all(class_= 'tweet-reply-context username')[0]
            areplyto = areplyto.find_all('a')[0]
            areplyto = bs(str(areplyto), "lxml").text.replace('@','')
        except:
            areplyto = ''         
        
        #RP = t.find_all('span',class_='ProfileTweet-actionCountForAria')[0]# Loading reply, retweet & Likes
        #replies.append(int((bs(str(RP), "lxml").text.split()[0]).replace('.','').replace(',','')))
        
        # Replies
        # Retweets
        # Likes
        
        tweet = t.find_all(class_= 'tweet-text')[0]
        tweet = bs(str(tweet),'html.parser').text.strip()
        
        if 'rt @' in tweet[:5].lower():
            isretweet = 1
        else:
            isretweet = 0
            
        url = str(t).split('\n')[0]
        mulai, akhir = url.find('href="/')+len('href="/'), url.find('">')
        url = 'https://twitter.com/' + url[mulai:akhir]
        posts.append({'time':wkt, 'username':usr, 'tweet':tweet, 'link':url, 'lat':'', 'lon':'', 'location':''})
    if posts:
        try:
            nextPage = soup.find_all(class_= 'w-button-more')[0]
            nextPage = str(nextPage).split('\n')[1]
            mulai, akhir = nextPage.find('href="/')+len('href="/'), nextPage.find('">')
            nextPage = 'https://twitter.com/' + nextPage[mulai:akhir]
        except:
            nextPage = None
    else:
        posts = None
    return posts, nextPage

"""
def reverseGeo(dbPar, gmaps, lan='id'):
    db = conMql(dbPar)
    qry = 'SELECT DISTINCT username, lat, lon FROM {}'.format(dbPar['tbl'])
    cur = db.cursor()
    cur.execute(qry)
    data = cur.fetchall()
    cur.close();db.close()
    for u, lat, lon in tqdm(data):
        #print(u, lat, lon)
        break
        #lokasi = []
        #res = gmaps.geolocate("{}, {}".format(lat,lon))
        
    return 0
"""    
    

def insertTweet(posts, dbPar):
    for p in posts:
        #break
        h = p['username'] + p['tweet']# + 'noise'
        h = hashlib.md5(h.encode()).hexdigest()
        #qry = 'SELECT EXISTS(SELECT 1 FROM {} WHERE tweet_hash ="{}" LIMIT 1)'.format(dbPar['tbl'], pymysql.escape_string(h))
        qry = "SELECT username FROM {} WHERE tweetID = '{}' LIMIT 1".format(dbPar['tbl'], h)
        db = conMql(dbPar)
        cur = db.cursor()
        cur.execute(qry)
        data = cur.fetchall()#[0][0]
        cur.close();db.close()
        if data:
            #print('hi')
            # u = 'ila_rizky' h = 'e2c74235b256d7d37cf4afa9c9320b2a'
            if p['lat'] != 0.0 or p['location'] != '':
                # check if users location = '' or null if yes update with data[location]
                """
                con = mysql.connector.connect(host=dbPar['host'],database=dbPar['db'],user=dbPar['usr'],password=dbPar['pass'])
                cursor = con.cursor()
                cursor.execute(qry)
                rows = cursor.fetchall()
                """
                qry = 'SELECT username, lat, lon, location FROM {} WHERE tweetID ={} LIMIT 1'.format(dbPar['tbl'], h)
                db = conMql(dbPar)
                cur = db.cursor()
                cur.execute(qry)
                dt = cur.fetchall()[0]
                cur.close();db.close()
                if dt[-1]=='' or dt[1]==0.0:
                    qry = 'UPDATE {} SET location="{}", lat={}, lon={} WHERE username="{}"'.format(dbPar['tbl'], p['location'], str(p['lat']), str(p['lon']), dt[0])
                    db = conMql(dbPar)
                    cur = db.cursor()
                    cur.execute(pymysql.escape_string(qry))
                    db.commit()
                    print(cur.rowcount, " record(s) updated")
                    cur.close();db.close()
            else:
                pass 
        else: #insert data
            try:
                db = conMql(dbPar)
                cur = db.cursor()
                qry = 'INSERT INTO {} (tweetID, date, username, tweet, URL, lat, lon, location) VALUES ("{}","{}","{}","{}","{}", {}, {}, "{}")'.\
                format(dbPar['tbl'], h, p['time'], p['username'], pyOld.escape_string(p['tweet']), pyOld.escape_string(p['link']), p['lat'], p['lon'], pyOld.escape_string(p['location']))
                cur.execute(qry)
                cur.close();db.close()
            except:
                print('query Error =\n{}'.format(qry))
    return True

def conMql(dbPar):
    server, usr, pas, dDb = dbPar['host'], dbPar['usr'], dbPar['pass'], dbPar['db']
    try:
        conMsq = pymysql.connect(host=server,user=usr,passwd=pas,db=dDb)
        return conMsq
    except (pymysql.Error) as e:      
        print ("Error Connecting to MySQL %d: %s" % (e.args[0],e.args[1]))
        sys.exit(1)
        
def streamTwitter(topicS, lang, Ck, Cs, At, As):
    class MyStreamer(TwythonStreamer):
        def on_success(self, data):
            print('tweet from {}, post: {}'.format(data['user']['screen_name'], data['text']))
        def on_error(self, status_code, data):
            print('Error Status = %s' %status_code); self.disconnect()

    print('Start Streaming Data, Please Wait ... ')
    stream = MyStreamer(Ck, Cs, At, As)
    stream.statuses.filter(track=topicS)
    
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

def loadSentimenCorpus(fPos, fNeg, fNegasi, fSuperlatif, fEmot):
    wPos = loadCorpus(file=fPos, dictionary = False)
    wNeg = loadCorpus(file=fNeg, dictionary = False)
    wordS = (wPos, wNeg)
    negasi = loadCorpus(file=fNegasi, dictionary = False)
    superlatif = loadCorpus(file=fSuperlatif, dictionary = False)
    emotS = loadCorpus(file=fEmot, sep='\t')
    for k,v in emotS.items():
        emotS[k] = int(v)
    return wordS, negasi, superlatif, emotS

def format_filename(s):
    """
    Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed. Also spaces are replaced with underscores.
     
    Note: this method may produce invalid filenames such as ``, `.` or `..`
    When I use this method I prepend a date string like '2009_01_15_19_46_32_'
    and append a file extension like '.txt', so I avoid the potential of using
    an invalid filename.
     
    """
    t = s.split('/')[-1].split('/')[-1].split('/')[-1][-32:]
    t = t.replace('\n', ' ').replace('\r', ' ').strip()
    t = re.sub(r'[^._a-zA-Z0-9 -\.]',' ', t)
    t = unescape(t) # html entities fix
    return unidecode(t)

def getFileType(url):
    types = ('php','htm','html','pdf','doc','docx','xls','xlsx','ppt','pptx', 'jpg', 'png', 'gif', 'bmp', 'ps', 'webp')
    for tipe in types:
        if '.'+tipe in url[-7:]:
            return tipe
    return 'php'

def fetch_results(search_term, number_results, language_code, headers = None, timeout=30):   
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=headers, timeout=timeout, verify=False) # timeout=15, verify=False
    response.raise_for_status()
    return search_term, response.text

def parse_results(html, keyword):
    soup = bs(html, 'html.parser')
    found_results = []
    rank = 1
    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:
        link = result.find('a', href=True)
        url = link.attrs['href']
        title = result.find('h3')
        description = result.find('span', attrs={'class': 'st'})
        if link and title:
            link = link['href']
            title = title.get_text()
            if description:
                description = description.get_text()
            if link != '#':
                found_results.append({'url':url, 'rank': rank, 'title': title, 'description': description})
                #found_results.append({'url':url, 'keyword': keyword, 'rank': rank, 'title': title, 'description': description})
                rank += 1
    return found_results

def scrape_google(search_term, number_results, language_code, headers = None):
    """
    https://edmundmartin.com/scraping-google-with-python/
    """
    try:
        keyword, html = fetch_results(search_term, number_results, language_code, headers = headers)
        results = parse_results(html, keyword)
        return results
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        raise Exception("You appear to have been blocked by Google")
    except requests.RequestException:
        raise Exception("Appears to be an issue with your connection")
        
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

def get_proxies():
    #from lxml.html import fromstring
    """
    https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/
    https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/
    import requests
    from lxml.html import fromstring
    """
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

def getSitePages(df, fix, path='data/', lemma=None, stops=None, sym=True, minC=3, maxC=12, fixMix=True):
    filters = set(['.jpg', '.png', '.gif', '.bmp', '.ps', '.webp'])
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    chunk_size = 128
    for i, row in tqdm(df.iterrows()):
        url = row.URL_clean.lower()
        aFile = [True for f in filters if f in url]
        if not aFile and 'pdfCached' not in row.Title and '[PDF]' not in row.Title:
            coba = 1
            while coba <3:
                try:
                    req = Request(url, headers = headers)
                    doc = urlopen(req).read()
                    doc = text_from_html(doc)
                    try:
                        doc.encode('utf-8')
                    except:
                        doc = ''
                    if doc:
                        doc = cleanText(doc, fix=fix, lemma=lemma, stops = stops, symbols_remove = sym, min_charLen = minC, max_charLen = maxC, fixTag= False, fixMix=fixMix)
                        df.at[i,'page'] = doc
                    else:
                        df.at[i,'page'] = doc
                    time.sleep(2)
                    break
                except:
                    coba += 1
                    time.sleep(10)
        elif '[PDF]' in row.Title[:7]:
            filename = path+url.split('/')[-1][-32:]
            r = requests.get(url, stream = True) 
            with open(filename,"wb") as pdf:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk: 
                        pdf.write(chunk)
            doc = readDocs(filename)
            if doc:
                doc = cleanText(doc, fix=fix, lemma=lemma, stops = stops, symbols_remove = sym, min_charLen = minC, max_charLen = maxC, fixTag= False, fixMix=fixMix)
                df.at[i,'page'] = doc
            else:
                pass
    return df

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = bs(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def loadCorpus(file='', sep=':', dictionary = True):
    file = open(file, 'r', encoding="utf-8", errors='replace')
    F = file.readlines()
    file.close()
    if dictionary:
        fix = {}
        for f in F:
            k, v = f.split(sep)
            k, v = k.strip(), v.strip()
            fix[k] = v
    else:
        fix = set( (w.strip().replace('\ufeff','') for w in F) )
    return fix

def cleanCorpus(file=''):
    """
    file = 'data/kataPosID.txt'
    file = 'data/kataNegID.txt'
    file = 'data/negasi.txt'
    file = 'data/slang.dic'
    """
    f = open(file, 'r', encoding="utf-8", errors='replace')
    F = f.readlines()
    f.close()
    fix = set( (w.strip() for w in F) )
    fix = list(fix)
    fix.sort()
    with open(file, 'w') as f:
        for kata in fix:
            try:
                f.write(kata+'\n')
            except:
                pass
    print(fix[:5], '\n', fix[-5:])
    return True

@timeout_decorator.timeout(20)
def readDocs(file):
    if 'pdf' in file:
        headers = {'X-Tika-PDFextractInlineImages': 'true',} 
        raw = parser.from_file(file, headers=headers)
    else:
        raw = parser.from_file(file)
    if 'content' in raw.keys():
        return raw['content']
    else:
        return None

def twitter_html2csv(fData, fHasil):
    urlPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    print('Loading Data: ', flush = True)
    Tweets, Username, waktu, replies, retweets, likes, Language, urlStatus =  [], [], [], [], [], [], [], []
    soup = bs(open(fData,encoding='utf-8', errors = 'ignore', mode='r'),'html.parser')
    data = soup.find_all('li', class_= 'stream-item')
    for i,t in tqdm(enumerate(data)):
        T = t.find_all('p',class_='TweetTextSize')[0] # Loading tweet
        Tweets.append(bs(str(T),'html.parser').text)
        U = t.find_all('span',class_='username')
        Username.append(bs(str(U[0]),'html.parser').text)
        T = t.find_all('a',class_='tweet-timestamp')[0]# Loading Time
        waktu.append(bs(str(T),'html.parser').text)
        RP = t.find_all('span',class_='ProfileTweet-actionCountForAria')[0]# Loading reply, retweet & Likes
        replies.append(int((bs(str(RP), "lxml").text.split()[0]).replace('.','').replace(',','')))
        RT = t.find_all('span',class_='ProfileTweet-actionCountForAria')[1]
        RT = int((bs(str(RT), "lxml").text.split()[0]).replace('.','').replace(',',''))
        retweets.append(RT)
        L  = t.find_all('span',class_='ProfileTweet-actionCountForAria')[2]
        likes.append(int((bs(str(L), "lxml").text.split()[0]).replace('.','').replace(',','')))
        try:# Loading Bahasa
            L = t.find_all('span',class_='tweet-language')
            Language.append(bs(str(L[0]), "lxml").text)
        except:
            Language.append('')
        url = str(t.find_all('small',class_='time')[0])
        try:
            url = re.findall(urlPattern,url)[0]
        except:
            try:
                mulai, akhir = url.find('href="/')+len('href="/'), url.find('" title=')
                url = 'https://twitter.com/' + url[mulai:akhir]
            except:
                url = ''
        urlStatus.append(url)
    print('Saving Data to "%s" ' %fHasil, flush = True)
    dfile = open(fHasil, 'w', encoding='utf-8', newline='')
    dfile.write('Time, Username, Tweet, Replies, Retweets, Likes, Language, urlStatus\n')
    with dfile:
        writer = csv.writer(dfile)
        for i,t in enumerate(Tweets):
            writer.writerow([waktu[i],Username[i],t,replies[i],retweets[i],likes[i],Language[i],urlStatus[i]])
    dfile.close()
    print('All Finished', flush = True)
    
def twitter_html2csv_bak(fData, fHasil):
    urlPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    print('Loading Data: ', flush = True)
    Tweets, Username, waktu, replies, retweets, likes, Language, urlStatus =  [], [], [], [], [], [], [], []
    soup = bs(open(fData,encoding='utf-8', errors = 'ignore', mode='r'),'html.parser')
    data = soup.find_all('li', class_= 'stream-item')
    for i,t in tqdm(enumerate(data)):
        T = t.find_all('p',class_='TweetTextSize')[0] # Loading tweet
        Tweets.append(bs(str(T),'html.parser').text)
        U = t.find_all('span',class_='username')
        Username.append(bs(str(U[0]),'html.parser').text)
        T = t.find_all('a',class_='tweet-timestamp')[0]# Loading Time
        waktu.append(bs(str(T),'html.parser').text)
        RP = t.find_all('span',class_='ProfileTweet-actionCountForAria')[0]# Loading reply, retweet & Likes
        replies.append(int((bs(str(RP), "lxml").text.split()[0]).replace('.','').replace(',','')))
        RT = t.find_all('span',class_='ProfileTweet-actionCountForAria')[1]
        RT = int((bs(str(RT), "lxml").text.split()[0]).replace('.','').replace(',',''))
        retweets.append(RT)
        L  = t.find_all('span',class_='ProfileTweet-actionCountForAria')[2]
        likes.append(int((bs(str(L), "lxml").text.split()[0]).replace('.','').replace(',','')))
        try:# Loading Bahasa
            L = t.find_all('span',class_='tweet-language')
            Language.append(bs(str(L[0]), "lxml").text)
        except:
            Language.append('')
        url = str(t.find_all('small',class_='time')[0])
        try:
            url = re.findall(urlPattern,url)[0]
        except:
            try:
                mulai, akhir = url.find('href="/')+len('href="/'), url.find('" title=')
                url = 'https://twitter.com/' + url[mulai:akhir]
            except:
                url = ''
        urlStatus.append(url)
    print('Saving Data to "%s" ' %fHasil, flush = True)
    dfile = open(fHasil, 'w', encoding='utf-8', newline='')
    dfile.write('Time, Username, Tweet, Replies, Retweets, Likes, Language, urlStatus\n')
    with dfile:
        writer = csv.writer(dfile)
        for i,t in enumerate(Tweets):
            writer.writerow([waktu[i],Username[i],t,replies[i],retweets[i],likes[i],Language[i],urlStatus[i]])
    dfile.close()
    print('All Finished', flush = True)

def twitter_connect(Ck, Cs, At, As):
    try:
        twitter = Twython(Ck, Cs, At, As)
        user = twitter.verify_credentials()
        print('Welcome "%s" you are now connected to twitter server' %user['name'])
        return twitter
    except:
        print("Connection failed, please check your API keys or connection")

def getLocation(twitter, gmaps, username):
    try:
        res = twitter.show_user(screen_name=username)
    except TwythonRateLimitError:
        print('\nRate Limit reached ... sleeping for 15 Minutes', flush = True)
        for itr in trange(15*60):
            time.sleep(1)
        res = twitter.show_user(screen_name=username)
    try:
        L = res['coordinates']['coordinates']
        lat, lon = L[0], L[1]
    except:
        lat, lon = None, None
    
    try:
        alamat = res['location']
    except:
        pass
    if alamat:
        try:
            time.sleep(2)
            res = gmaps.geocode(alamat)[0]
            if not lat and not lon:
                latlon = res['geometry']['location']
                lat, lon = latlon['lat'], latlon['lng']
        except:
            pass
        try:
            alamat = [alamat]
            addresses = res['address_components']
            for a in addresses:
                alamat.append(a['long_name'])
            alamat = ' '.join(alamat)
        except:
            pass
    return alamat, lat, lon

def getTweets(twitter, topic, N = 100, lan = None):
    Tweets, MAX_ATTEMPTS, count, dBreak, next_max_id = [], 3, 0, False, 0
    for i in range(MAX_ATTEMPTS):
        if(count>=N or dBreak):
            print('\nFinished importing %.0f' %count);break
        if(i == 0):
            if lan:
                results=twitter.search(q=topic, lang=lan, count=100, tweet_mode = 'extended')
            else:
                results=twitter.search(q=topic, count=100, tweet_mode = 'extended')

            Tweets.extend(results['statuses'])
            count += len(results['statuses'])
            if count>N:
                print("\rNbr of Tweets captured: {}".format(N), end="")
                Tweets = Tweets[:N]
                dBreak = True; break
            else:
                print("\rNbr of Tweets captured: {}".format(count), end="")

        else:
            try:
                if lan:
                    results=twitter.search(q=topic,include_entities='true',max_id=next_max_id, lang=lan, count=100, tweet_mode = 'extended')
                else:
                    results=twitter.search(q=topic,include_entities='true',max_id=next_max_id, count=100, tweet_mode = 'extended')

                Tweets.extend(results['statuses'])
                count += len(results['statuses'])
                if count>N:
                    print("\rNbr of Tweets captured: {}".format(N), end="")
                    Tweets = Tweets[:N]
                    dBreak = True; break
                else:
                    print("\rNbr of Tweets captured: {}".format(count), end="")

                try:
                    next_results_url_params=results['search_metadata']['next_results']
                    next_max_id=next_results_url_params.split('max_id=')[1].split('&')[0]
                except:
                    print('\nFinished, no more tweets available for query "%s"' %str(topic), flush = True)
                    dBreak = True; break

            except TwythonRateLimitError:
                print('\nRate Limit reached ... sleeping for 15 Minutes', flush = True)
                for itr in trange(15*60):
                    time.sleep(1)
            except:
                print('\nSomething is not right, retrying ... (attempt = {}/{})'.format(i+1,MAX_ATTEMPTS), flush = True)
    return Tweets

def saveTweets(Tweets,file='Tweets.json', plain = False): #in Json Format
    with open(file, 'w') as f:
        for T in Tweets:
            if plain:
                f.write(T+'\n')
            else:
                try:
                    f.write(json.dumps(T)+'\n')
                except:
                    pass

def loadTweets(file='Tweets.json'):
    f=open(file,encoding='utf-8', errors ='ignore', mode='r');T=f.readlines();f.close()
    for i,t in enumerate(T):
        T[i] = json.loads(t.strip())
    return T

def LoadStopWords(lang='en'):
    L = lang.lower().strip()
    if L == 'en' or L == 'english' or L == 'inggris':
        from spacy.lang.en import English as lemmatizer
        #lemmatizer = spacy.lang.en.English
        lemmatizer = lemmatizer()
        #lemmatizer = spacy.load('en')
        stops =  set([t.strip() for t in LoadDocuments(file = 'data/stopwords_eng.txt')[0]])
    elif L == 'id' or L == 'indonesia' or L=='indonesian':
        from spacy.lang.id import Indonesian
        #lemmatizer = spacy.lang.id.Indonesian
        lemmatizer = Indonesian()
        stops = set([t.strip() for t in LoadDocuments(file = 'data/stopwords_id.txt')[0]])
    else:
        print('Warning, language not recognized. Empty StopWords Given')
        stops = set(); lemmatizer = None
    return stops, lemmatizer    

def cleanText(T, fix={}, lemma=None, stops = set(), symbols_remove = True, min_charLen = 2, max_charLen = 15, fixTag= False, fixMix=True):
    # lang & stopS only 2 options : 'en' atau 'id'
    # symbols ASCII atau alnum
    #T = 'kupu-kupu warna biru, abu-abu.'
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    t = re.sub(pattern,' ',T) #remove urls if any
    pattern = re.compile(r'ftp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    t = re.sub(pattern,' ',t) #remove urls if any
    t = unescape(t) # html entities fix
    if fixTag:
        t = fixTags(t) # fix abcDef
    t = t.lower().strip() # lowercase
    t = unidecode(t)
    t = ''.join(''.join(s)[:2] for _, s in itertools.groupby(t)) # remove repetition
    t = t.replace('\n', ' ').replace('\r', ' ')
    t = sent_tokenize(t) # sentence segmentation. String to list
    for i, K in enumerate(t):
        if symbols_remove:
            K = re.sub(r'[^.,_a-zA-Z0-9 -\.]',' ',K)
        if lemma:
            listKata = lemma(K)
        else:
            listKata = TextBlob(K).words
        cleanList = []
        for token in listKata:
            if lemma:
                if str(token.text) in fix.keys():
                    token = fix[str(token.text)]
                try:
                    token = token.lemma_
                except:
                    token = lemma(token)[0].lemma_
            else:
                if str(token) in fix.keys():
                    token = fix[str(token)]
            if stops:
                if len(token)>=min_charLen and token not in stops:
                    if fixMix and str(token.replace(' ','').replace('-','a')).isalpha():
                        cleanList.append(token)
                    elif not fixMix:
                        cleanList.append(token)
            else:
                if len(token)>=min_charLen:
                    if fixMix and str(token.replace(' ','').replace('-','a')).isalpha():
                        cleanList.append(token)
                    elif not fixMix:
                        cleanList.append(token)
        t[i] = ' '.join(cleanList)
    return ' '.join(t) # Return kalimat lagi


def crawlFiles(dPath,types=None): # dPath ='C:/Temp/', types = 'pdf'
    if types:
        return [str(dPath+'/'+f).replace('\\','/') for f in os.listdir(dPath) if f.endswith('.'+types)]
    else:
        return [str(dPath+'/'+f).replace('\\','/') for f in os.listdir(dPath)]

def LoadDocuments(dPath=None,types=None, file = None): # types = ['pdf','doc','docx','txt','bz2']
    Files, Docs = [], []
    if types:
        for tipe in types:
            Files += crawlFiles(dPath,tipe)
    if file:
        Files = [file]
    if not types and not file: # get all files regardless of their extensions
        Files += crawlFiles(dPath)
    for f in Files:
        if f[-3:].lower() in ['txt', 'dic','py', 'ipynb']:
            try:
                df=open(f,"r",encoding="utf-8", errors='replace')
                Docs.append(df.readlines());df.close()
            except:
                print('error reading{0}'.format(f))
        elif f[-3:].lower()=='bz2':
            try:
                Docs.append(readBz2(f))
            except:
                print('error reading{0}'.format(f))
        elif f[-3:].lower()=='csv':
            Docs.append(pd.read_csv(f))
        else:
            print('Unsupported format {0}'.format(f))
    if file:
        Docs = Docs[0]
    return Docs, Files

def readBz2(file):
    with bz2(file, "r") as bzData:
        txt = []
        for line in bzData:
            try:
                txt.append(line.strip().decode('utf-8','replace'))
            except:
                pass
    return ' '.join(txt)

def countWords(Doc):
    Full_Tokens  = []
    for line in Doc:
        Full_Tokens.append(TextBlob(line.lower()).words)
    Full_Tokens = [kata for line in Full_Tokens for kata in line] # Flatten List
    Words = Counter(Full_Tokens)
    Words = [(kata,freq) for kata,freq in Words.items()]
    Words.sort(key=lambda tup: tup[1])
    Words = Words[::-1] # Reverse = Descending
    frekuensi = [f[1] for f in Words]
    kata = [f[0] for f in Words]
    return kata, frekuensi

def barChart(kata,frekuensi,N=100):
    y_pos = np.arange(len(kata[:N]))
    plt.bar(y_pos, frekuensi[:N], align='center', alpha=0.5)
    plt.xticks(y_pos, kata)
    plt.ylabel('Frekuensi')
    plt.title('Token')
    plt.show()


def Zipf(frekuensi, par=2, nBins = 100, yScale=0.05):
    count, bins, ignored = plt.hist(np.array(frekuensi), nBins, normed=True)
    plt.title("Zipf plot")
    x = np.arange(1., nBins)
    plt.xlabel("Frequency Rank of Token")
    y = x**(-par) / special.zetac(par)
    plt.ylabel("Absolute Frequency of Token")
    plt.plot(x, y*yScale/max(y), linewidth=2, color='r')
    plt.show()

def WordNet_id(f1 = 'data/wn-ind-def.tab', f2 = 'data/wn-msa-all.tab'):
    w1, wn_id = {}, {}
    df=open(f1,"r",encoding="utf-8", errors='replace')
    d1=df.readlines();df.close()
    df=open(f2,"r",encoding="utf-8", errors='replace')
    d2=df.readlines();df.close(); del df
    for line in d1:
        data = line.split('\t')
        w1[data[0].strip()] = data[-1].strip()
    for line in d2:
        data = line.split('\t')
        kata = data[-1].strip()
        kode = data[0].strip()
        if data[1].strip()=="I":
            if kode in w1.keys():
                if kata in wn_id:
                    wn_id[kata]['def'].append(w1[kode])
                    wn_id[kata]['pos'].append(kode[-1])
                else:
                    wn_id[kata] = {}
                    wn_id[kata]['def'] = [w1[kode]]
                    wn_id[kata]['pos'] = [kode[-1]]
            #else:
            #    wn_id[kata] = {}
            #    wn_id[kata]['def'] = ['']
            #    wn_id[kata]['pos'] = [kode[-1]]
    return wn_id

def loadPos_id(file = 'data/kata_dasar.txt'):
    kata_pos = {}
    df=open(file,"r",encoding="utf-8", errors='replace')
    data=df.readlines();df.close()
    for line in data:
        d = line.split()
        kata = d[0].strip()
        pos = d[-1].strip().replace("(",'').replace(')','')
        kata_pos[kata] = pos
    return kata_pos

def lesk_wsd(sentence, ambiguous_word, pos=None, stem=True, hyperhypo=True):
    # https://en.wikipedia.org/wiki/Lesk_algorithm
    # https://stackoverflow.com/questions/20896278/word-sense-disambiguation-algorithm-in-python
    max_overlaps = 0; lesk_sense = None
    context_sentence = sentence.split()
    for ss in wn.synsets(ambiguous_word):
        #break
        if pos and ss.pos is not pos: # If POS is specified.
            continue
        lesk_dictionary = []
        lesk_dictionary+= ss.definition().replace('(','').replace(')','').split() # Includes definition.
        lesk_dictionary+= ss.lemma_names() # Includes lemma_names.
        # Optional: includes lemma_names of hypernyms and hyponyms.
        if hyperhypo == True:
            lesk_dictionary+= list(chain(*[i.lemma_names() for i in ss.hypernyms()+ss.hyponyms()]))

        if stem == True: # Matching exact words causes sparsity, so lets match stems.
            lesk_dictionary = [ps.stem(i) for i in lesk_dictionary]
            context_sentence = [ps.stem(i) for i in context_sentence]

        overlaps = set(lesk_dictionary).intersection(context_sentence)

        if len(overlaps) > max_overlaps:
            lesk_sense = ss
            max_overlaps = len(overlaps)
    return lesk_sense.name()

def words(text): return re.findall(r'\w+', text.lower())

corpus = 'data/kata_dasar.txt'
WORDS = Counter(words(open(corpus).read()))

def P(word):
    "Probability of `word`."
    N=sum(WORDS.values())
    return WORDS[word] / N

def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word):
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def saveTweets_old(Tweets,file='Tweets.json', plain = False): #in "Json" Format or "txt" in plain type
    with open(file, 'w') as f:
        for T in Tweets:
            if plain:
                try:
                    f.write(T['nlp']+'\n')
                except:
                    f.write(T['fullTxt']+'\n')
            else:
                try:
                    f.write(json.dumps(T)+'\n')
                except:
                    pass

def loadTweets_old(file):
    f=open(file,encoding='utf-8', errors ='ignore', mode='r');T=f.readlines();f.close()
    for i,t in enumerate(T):
        T[i] = json.loads(t.strip())
    return T

def strip_non_ascii(string,symbols):
    ''' Returns the string without non ASCII characters''' #isascii = lambda s: len(s) == len(s.encode())
    stripped = (c for c in string if 0 < ord(c) < 127 and c not in symbols)
    return ''.join(stripped)

def adaAngka(s):
    return any(i.isdigit() for i in s)

def fixTags(t):
    getHashtags = re.compile(r"#(\w+)")
    pisahtags = re.compile(r'[A-Z][^A-Z]*')
    tagS = re.findall(getHashtags, t)
    for tag in tagS:
        if len(tag)>0:
            tg = tag[0].upper()+tag[1:]
            proper_words = []
            if adaAngka(tg):
                tag2 = re.split('(\d+)',tg)
                tag2 = [w for w in tag2 if len(w)>0]
                for w in tag2:
                    try:
                        _ = int(w) # error if w not a number
                        proper_words.append(w)
                    except:
                        w = w[0].upper()+w[1:]
                        proper_words = proper_words+re.findall(pisahtags, w)
            else:
                proper_words = re.findall(pisahtags, tg)
            proper_words = ' '.join(proper_words)
            t = t.replace('#'+tag, proper_words)
    return t

def we2vsm(model_we, data_we):
    N = len(data_we)
    L = model_we.vector_size
    vsm_we = np.empty([N, L], dtype=np.float64) # inisialisasi matriks
    for i,d in tqdm(enumerate(data_we)):
        tmp = np.zeros([1, L], dtype=np.float64)
        count = 0
        for t in d:
            try:
                tmp += model_we.wv.__getitem__([t])
                count += 1
            except:
                pass
        if count>0:
            vsm_we[i] = tmp/count
    return vsm_we

def cleanTweets(Tweets):
    factory = StopWordRemoverFactory(); stopwords = set(factory.get_stop_words()+['twitter','rt','pic','com','yg','ga','https'])
    factory = StemmerFactory(); stemmer = factory.create_stemmer()
    for i,tweet in enumerate(tqdm(Tweets)):
        txt = tweet['fullTxt'] # if you want to ignore retweets  ==> if not re.match(r'^RT.*', txt):
        txt = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',' ',txt)# clean urls
        txt = txt.lower() # Lowercase
        txt = Tokenizer.tokenize(txt)
        symbols = set(['@']) # Add more if you want
        txt = [strip_non_ascii(t,symbols) for t in txt] #remove all non ASCII characters
        txt = ' '.join([t for t in txt if len(t)>1])
        Tweets[i]['cleanTxt'] = txt # this is not a good Python practice, only for learning.
        txt = stemmer.stem(txt).split()
        Tweets[i]['nlp'] = ' '.join([t for t in txt if t not in stopwords])
    return Tweets

def translate(txt,language='en'): # txt is a TextBlob object
    try:
        return txt.translate(to=language)
    except:
        return txt

def sentiment_older(Tweets): #need a clean tweets
    print("Calculating Sentiment and Subjectivity Score: ... ")
    T = [translate(TextBlob(tweet['cleanTxt'])) for tweet in tqdm(Tweets)]
    Sen = [tweet.sentiment.polarity for tweet in tqdm(T)]
    Sub = [float(tweet.sentiment.subjectivity) for tweet in tqdm(T)]
    Se, Su = [], []
    for score_se, score_su in zip(Sen,Sub):
        if score_se>0.1:
            Se.append('pos')
        elif score_se<-0.05: #I prefer this
            Se.append('neg')
        else:
            Se.append('net')
        if score_su>0.5:
            Su.append('Subjektif')
        else:
            Su.append('Objektif')
    label_se = ['Positif','Negatif', 'Netral']
    score_se = [len([True for t in Se if t=='pos']),len([True for t in Se if t=='neg']),len([True for t in Se if t=='net'])]
    label_su = ['Subjektif','Objektif']
    score_su = [len([True for t in Su if t=='Subjektif']),len([True for t in Su if t=='Objektif'])]
    PieChart(score_se,label_se); PieChart(score_su,label_su)
    Sen = [(s,t['fullTxt']) for s,t in zip(Sen,Tweets)]
    Sen.sort(key=lambda tup: tup[0])
    Sub = [(s,t['fullTxt']) for s,t in zip(Sub,Tweets)]
    Sub.sort(key=lambda tup: tup[0])
    return (Sen, Sub)

def sentiment_old(D): #need a clean tweets
    print("Calculating Sentiment and Subjectivity Score: ... ")
    T = [translate(TextBlob(t)) for t in tqdm(D)]
    Sen = [tweet.sentiment.polarity for tweet in tqdm(T)]
    Sub = [float(tweet.sentiment.subjectivity) for tweet in tqdm(T)]
    Se, Su = [], []
    for score_se, score_su in zip(Sen,Sub):
        if score_se>0.0:
            Se.append('pos')
        elif score_se<0.0: #I prefer this
            Se.append('neg')
        else:
            Se.append('net')
        if score_su>0.5:
            Su.append('Subjektif')
        else:
            Su.append('Objektif')
    label_se = ['Positif','Negatif', 'Netral']
    score_se = [len([True for t in Se if t=='pos']),len([True for t in Se if t=='neg']),len([True for t in Se if t=='net'])]
    label_su = ['Subjektif','Objektif']
    score_su = [len([True for t in Su if t=='Subjektif']),len([True for t in Su if t=='Objektif'])]
    PieChart(score_se,label_se); PieChart(score_su,label_su)
    Sen = [(s,t) for s,t in zip(Sen,D)]
    Sen.sort(key=lambda tup: tup[0])
    Sub = [(s,t) for s,t in zip(Sub,D)]
    Sub.sort(key=lambda tup: tup[0])
    return (Sen, Sub)

def SentimentPie(D, wordS, emotS=(), negasi=(), superlatif = ()):
    Se, scoreS = [], []
    label_se = ['Positif','Negatif', 'Netral']
    for d in tqdm(D):
        sentiment, score = Sentiment(d, wordS, emotS=emotS, negasi=negasi, superlatif = superlatif)
        Se.append(sentiment)
        scoreS.append(score)
    score_se = [len([True for t in Se if t=='pos']),len([True for t in Se if t=='neg']),len([True for t in Se if t=='net'])]
    #Sen = [(sc, s) for sc, s in zip(scoreS, Se)]
    #Sen.sort(key=lambda tup: tup[0], reverse = True)
    #Score = [t[0] for t in Sen]; #Sen = [t[1] for t in Sen]
    PieChart(score_se, label_se)
    plt.show()
    return Se, scoreS

def Sentiment(kalimat, wordS, emotS=(), negasi=(), superlatif = ()):
    """
    fEmot = 'data/emoticon.txt'
    fPos = 'data/kataPosID.txt'
    fNeg = 'data/kataNegID.txt'
    fNegasi = 'data/negasi.txt'
    wPos = loadCorpus(file=fPos, dictionary = False)
    wNeg = loadCorpus(file=fNeg, dictionary = False)
    wordS = (wPos, wNeg)
    negasi = loadCorpus(file=fNegasi, dictionary = False)
    emotS = loadCorpus(file=fEmot, sep='\t')
    for k,v in emotS.items():
        emotS[k] = int(v)
    D = ('Mie Ayam enak', 'dodol ga enak', 'ini apaan sih?', 'halo')
    Sen, Score = tau.SentimentPie(D, wordS, emotS=emotS, negasi=negasi)
    
    **PR** tambahkan superlative words: sangat, banget, sekali, etc di Depan dan Belakang
    """
    wPos, wNeg = wordS
    posWords, negWords = [], []
    
    if emotS:
        for k,v in emotS.items():
            if k in kalimat:
                if emotS[k] > 0:
                    posWords.append(k)
                else:
                    negWords.append(k)
    
    K = simpleClean(kalimat)
    for w in wPos:
        if w in K:
            for ww in negasi:
                kebalikan = False
                inverted = ww+' '+w
                if inverted in K:
                    negWords.append(inverted)
                    kebalikan = True
                    break
            if not kebalikan:
                posWords.append(w)
    for w in wNeg:
        if w in K:
            for ww in negasi:
                kebalikan = False
                inverted = ww+' '+w
                if inverted in K:
                    posWords.append(inverted)
                    kebalikan = True
                    break
            if not kebalikan:
                negWords.append(w)
    
    for w in posWords:
        for ww in superlatif:
            superFront = ww+' '+w
            superBack = w+' '+ww
            if superFront in K:
                posWords.append(superFront)
                break
            elif superBack in K:
                posWords.append(superBack)
                break
            
    for w in negWords:
        for ww in superlatif:
            superFront = ww+' '+w
            superBack = w+' '+ww
            if superFront in K:
                negWords.append(superFront)
                break
            elif superBack in K:
                negWords.append(superBack)
                break            
    
    nPos, nNeg = len(posWords), len(negWords)
    sum_ = nPos + nNeg
    if sum_ == 0 or nPos==nNeg:
        return 'net', 0.0
    else:
        nPos, nNeg = nPos/sum_, nNeg/sum_
        if nPos>nNeg and nPos>0.05:
            return 'pos', nPos
        elif nNeg>nPos and nNeg>0.05:
            return 'neg', -nNeg
        else:
            return 'net', (nPos - nNeg)/2

def simpleClean(T):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    t = re.sub(pattern,' ',T) #remove urls if any
    pattern = re.compile(r'ftp[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    t = re.sub(pattern,' ',t) #remove urls if any
    t = unescape(t) # html entities fix
    t = t.lower().strip() # lowercase
    t = unidecode(t)
    t = ''.join(''.join(s)[:2] for _, s in itertools.groupby(t)) # remove repetition
    t = t.replace('\n', ' ').replace('\r', ' ')
    return re.sub(r'[^.,_a-zA-Z0-9 -\.]',' ',t)


def printSA(Sen, N = 2, emo = 'positif'):
    e = emo.lower().strip()
    if e=='positif' or e=='positive':
        tweets = Sen[-N:]
    elif e=='negatif' or e=='negative':
        tweets = Sen[:N]
    elif e=='netral' or e=='neutral':
        net = [(abs(score),t) for score,t in Sen if abs(score)<0.01]
        net.sort(key=lambda tup: tup[0])
        tweets = net[:N]
    else:
        print('Wrong function input parameter = "{0}"'.format(emo)); tweets=[]
    print('"{0}" Tweets = '.format(emo))
    for t in tweets:
        print(t)

def wordClouds(Tweets, file = 'wordCloud.png', plain = False, stopwords=None):
    if plain: # ordinary (large) Text file - String
        txt = Tweets
    else:
        txt = [t['full_text'] for t in Tweets]
    txt = ' '.join(txt)
    if stopwords:
        s = set(stopwords)
        for kata in s:
            txt = txt.replace(kata,' ')
    wc = WordCloud(background_color="white")#, max_font_size=40
    wordcloud = wc.generate(txt)
    plt.figure(num=1, facecolor='w', edgecolor='k') #figsize=(4, 3), dpi=600, #wc.to_file('wordCloud.png')
    plt.imshow(wordcloud, cmap=plt.cm.jet, interpolation='nearest', aspect='auto'); plt.xticks(()); plt.yticks(())
    #plt.savefig('wordCloud.png',bbox_inches='tight', pad_inches = 0.1, dpi=300)
    plt.show()

def PieChart(score,labels):
    fig1 = plt.figure(); fig1.add_subplot(111)
    plt.pie(score, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal');plt.show()
    return None

def drawGraph(G, Label, layOut='spring'):
    fig3 = plt.figure(); fig3.add_subplot(111)
    if layOut.lower()=='spring':
        pos = nx.spring_layout(G)
    elif layOut.lower()=='circular':
        pos=nx.circular_layout(G)
    elif layOut.lower()=='random':
        pos = nx.random_layout(G)
    elif layOut.lower()=='shells':
        shells = [G.core_nodes,sorted(G.major_building_routers, key=lambda n: nx.degree(G.topo, n)) + G.distribution_routers + G.server_nodes,G.hosts + G.minor_building_routers]
        pos = nx.shell_layout(G, shells)
    elif layOut.lower()=='spectral':
        pos=nx.spectral_layout(G)
    else:
        print('Graph Type is not available.')
        return
    nx.draw_networkx_nodes(G,pos, alpha=0.2,node_color='blue',node_size=600)
    if Label:
        nx.draw_networkx_labels(G,pos)
    nx.draw_networkx_edges(G,pos,width=4)
    plt.show()

def Graph(Tweets, Label = False, layOut='spring'): # Need the Tweets Before cleaning
    print("Please wait, building Graph .... ")
    G=nx.Graph()
    for tweet in tqdm(Tweets):
        if tweet['user']['screen_name'] not in G.nodes():
            G.add_node(tweet['user']['screen_name'])
        mentionS =  re.findall("@([a-zA-Z0-9]{1,15})", tweet['full_text'])
        for mention in mentionS:
            if "." not in mention: #skipping emails
                usr = mention.replace("@",'').strip()
                if usr not in G.nodes():
                    G.add_node(usr)
                G.add_edge(tweet['user']['screen_name'],usr)
    Nn, Ne = G.number_of_nodes(), G.number_of_edges()
    drawGraph(G, Label, layOut)
    print('Finished. There are %d nodes and %d edges in the Graph.' %(Nn,Ne))
    return G

def Centrality(G, N=10, method='katz', outliers=False, Label = True, layOut='shells'):

    if method.lower()=='katz':
        phi = 1.618033988749895 # largest eigenvalue of adj matrix
        ranking = nx.katz_centrality_numpy(G,1/phi)
    elif method.lower() == 'degree':
        ranking = nx.degree_centrality(G)
    elif method.lower() == 'eigen':
        ranking = nx.eigenvector_centrality_numpy(G)
    elif method.lower() =='closeness':
        ranking = nx.closeness_centrality(G)
    elif method.lower() =='betweeness':
        ranking = nx.betweenness_centrality(G)
    elif method.lower() =='harmonic':
        ranking = nx.harmonic_centrality(G)
    elif method.lower() =='percolation':
        ranking = nx.percolation_centrality(G)
    else:
        print('Error, Unsupported Method.'); return None

    important_nodes = sorted(ranking.items(), key=operator.itemgetter(1))[::-1]#[0:Nimportant]
    data = np.array([n[1] for n in important_nodes])
    dnodes = [n[0] for n in important_nodes][:N]
    if outliers:
        m = 1 # 1 standard Deviation CI
        data = data[:N]
        out = len(data[abs(data - np.mean(data)) > m * np.std(data)]) # outlier within m stDev interval
        if out<N:
            dnodes = [n for n in dnodes[:out]]

    print('Influencial Users: {0}'.format(str(dnodes)))
    print('Influencial Users Scores: {0}'.format(str(data[:len(dnodes)])))
    Gt = G.subgraph(dnodes)
    return Gt

def Community(G):
    part = community.best_partition(G)
    values = [part.get(node) for node in G.nodes()]
    mod, k = community.modularity(part,G), len(set(part.values()))
    print("Number of Communities = %d\nNetwork modularity = %.2f" %(k,mod)) # https://en.wikipedia.org/wiki/Modularity_%28networks%29
    fig2 = plt.figure(); fig2.add_subplot(111)
    nx.draw_shell(G, cmap = plt.get_cmap('gist_ncar'), node_color = values, node_size=30, with_labels=False)
    plt.show
    return values

def print_Topics(model, feature_names, Top_Topics, n_top_words):
    for topic_idx, topic in enumerate(model.components_[:Top_Topics]):
        print("Topic #%d:" %(topic_idx+1))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))

def getTopics(Txt,n_topics=5, Top_Words=7):
    tf_vectorizer = CountVectorizer(strip_accents = 'unicode', token_pattern = r'\b[a-zA-Z]{3,}\b', max_df = 0.95, min_df = 2)
    dtm_tf = tf_vectorizer.fit_transform(Txt)
    tf_terms = tf_vectorizer.get_feature_names()
    lda_tf = LDA(n_components=n_topics, learning_method='online', random_state=0).fit(dtm_tf)
    vsm_topics = lda_tf.transform(dtm_tf); doc_topic =  [a.argmax()+1 for a in tqdm(vsm_topics)] # topic of docs
    print('In total there are {0} major topics, distributed as follows'.format(len(set(doc_topic))))
    fig4 = plt.figure(); fig4.add_subplot(111)
    plt.hist(np.array(doc_topic), alpha=0.5); plt.show()
    print('Printing top {0} Topics, with top {1} Words:'.format(n_topics, Top_Words))
    print_Topics(lda_tf, tf_terms, n_topics, Top_Words)
    return lda_tf, dtm_tf, tf_vectorizer

def get_nMax(arr, n):
    indices = arr.ravel().argsort()[-n:]
    indices = (np.unravel_index(i, arr.shape) for i in indices)
    return [(arr[i], i) for i in indices]

def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]

def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def lDistance(firstString, secondString):
    "Function to find the Levenshtein distance between two words/sentences - gotten from http://rosettacode.org/wiki/Levenshtein_distance#Python"
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
        distances = newDistances
    return distances[-1]

def buildGraph(nodes):
    "nodes - list of hashables that represents the nodes of the graph"
    gr = nx.Graph() #initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    #add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr

def kataKunci(text):
    #tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)
    #assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]

    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

   #this will be used to determine adjacent words in order to construct keyphrases with two words

    graph = buildGraph(word_set_list)
    #pageRank - initial value of 1.0, error tolerance of 0,0001,
    calculated_page_rank = nx.pagerank(graph, weight='weight')
    #most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
    #the number of keyphrases returned will be relative to the size of the text (a third of the number of vertices)
    aThird = len(word_set_list) / 3
    keyphrases = keyphrases[0:aThird+1]

    #take keyphrases with multiple words into consideration as done in the paper - if two words are adjacent in the text and are selected as keywords, join them
    #together
    modifiedKeyphrases = set([])
    dealtWith = set([]) #keeps track of individual keywords that have been joined to form a keyphrase
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith:
                modifiedKeyphrases.add(firstWord)

            #if this is the last word in the text, and it is a keyword,
            #it definitely has no chance of being a keyphrase at this point
            if j == len(textlist)-1 and secondWord in keyphrases and secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)

        i = i + 1
        j = j + 1

    return modifiedKeyphrases

def Rangkum(text,M):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    graph = buildGraph(sentenceTokens)
    calculated_page_rank = nx.pagerank(graph, weight='weight')
    #most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
    #return a 100 word summary
    summary = ' '.join(sentences[:M])
    summaryWords = summary.split()
    summaryWords = summaryWords[0:101]
    summary = ' '.join(summaryWords)
    return summary