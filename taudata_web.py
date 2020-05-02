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
import os
import requests#, googlemaps
from bs4 import BeautifulSoup as bs
from bs4.element import Comment
from nltk.tokenize import TweetTokenizer; Tokenizer = TweetTokenizer(reduce_len=True)
from textblob import TextBlob
import re
import itertools
from nltk.stem import PorterStemmer;ps = PorterStemmer()
from html import unescape
from nltk import sent_tokenize
from unidecode import unidecode
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from spacy.lang.id import Indonesian
from nltk.tag import CRFTagger
nlp_id = Indonesian();ct = CRFTagger()  # Language Model
fTagger = 'data/all_indo_man_tag_corpus_model.crf.tagger'
ct.set_model_file(fTagger)

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
    return headers

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

def crawlFiles(dPath,types=None): # dPath ='C:/Temp/', types = 'pdf'
    if types:
        return [dPath+f for f in os.listdir(dPath) if f.endswith('.'+types)]
    else:
        return [dPath+f for f in os.listdir(dPath)]
    
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
        else:
            print('Unsupported format {0}'.format(f))
    if file:
        Docs = Docs[0]
    return Docs, Files

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

def cleanText(T, fix={}, lemma=None, stops = set(), symbols_remove = False, min_charLen = 2, max_charLen = 15, fixTag= False, fixMix=True):
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
    return '. '.join(t) # Return kalimat lagi



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
