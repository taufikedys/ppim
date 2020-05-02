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
import pandas as pd, numpy as np, seaborn as sns; sns.set()
from tqdm import tqdm
import requests
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob
from sklearn.decomposition import LatentDirichletAllocation as LDA
import re, matplotlib.pyplot as plt, os
import itertools
from html import unescape
from nltk import sent_tokenize
from unidecode import unidecode
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from gensim.models.ldamodel import LdaModel
from gensim.models.coherencemodel import CoherenceModel
from spacy.lang.id import Indonesian
from nltk.tag import CRFTagger

nlp_id = Indonesian();ct = CRFTagger()  # Language Model
fTagger = 'data/all_indo_man_tag_corpus_model.crf.tagger'
ct.set_model_file(fTagger)
    
def NLPfilter(t, filters):
    tokens = nlp_id(t)
    tokens = [str(k) for k in tokens if len(k)>2]
    hasil = ct.tag_sents([tokens])
    return [k[0] for k in hasil[0] if k[1] in filters]

def compute_coherence_values(dictionary, corpus, texts, limit, coherence='c_v', start=2, step=3):
    coherence_values = []
    model_list = []
    for num_topics in tqdm(range(start, limit, step)):
        model=LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence=coherence)
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values

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
                        _ = int(w)
                        proper_words.append(w)
                    except:
                        w = w[0].upper()+w[1:]
                        proper_words = proper_words+re.findall(pisahtags, w)
            else:
                proper_words = re.findall(pisahtags, tg)
            proper_words = ' '.join(proper_words)
            t = t.replace('#'+tag, proper_words)
    return t

def cleanText(T, fix={}, lemma=None, stops = set(), symbols_remove = True, min_charLen = 2, max_charLen = 15, fixTag= False, fixMix=True):
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
        elif f[-3:].lower()=='csv':
            Docs.append(pd.read_csv(f))
        else:
            print('Unsupported format {0}'.format(f))
    if file:
        Docs = Docs[0]
    return Docs, Files

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
