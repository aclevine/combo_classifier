'''
Created on May 19, 2014

@author: aclevine
'''
#===============================================================================
from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus.reader import CategorizedPlaintextCorpusReader
import nltk
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures, TrigramCollocationFinder, TrigramAssocMeasures
import itertools
import random
from nltk.stem.porter import PorterStemmer
import os
import string
import pickle
import re

from corpus import *
from nltk.corpus import stopwords
#===============================================================================
extra_sw = ['ga', 'enron.com', '@', ':', '-', ',' 'x', '.', 'the', 'a', 'in',
             'that', 'to', 'of', 'is', 'at', 'subject', 'body', '=', 'and', 'enron',
             's', ',', "'", '"', 'the', "'s", "''", '...', '--', '``', 'company', 'mr.', "n't"]
stopwords = set(extra_sw).union( nltk.corpus.stopwords.words('english') ).union(string.punctuation)

day_terms = set(['mon', 'monday', 'tues', 'tuesday', 'wed', 'wednesday', 'thurs', 'thursday', 'fri'
                'friday', 'sat', 'saturday', 'sun', 'sunday',
                'mondays', 'tuesdays', 'wednesdays', 'thursdays', 'fridays', 'saturdays', 'sundays'])

month_terms = set(['jan', 'january', 'feb', 'february', 'mar', 'march', 'apr', 'april', 'may',
                    'jun', 'june', 'jul', 'july', 'aug', 'august', 'sep', 'september', 'oct',
                    'october', 'nov', 'november', 'dec', 'december'])

time_terms = set(['noon', 'tonight', 'midnight', 'afternoon', 'morning', 'evening', 'pm'])

all_terms = time_terms.union(month_terms).union(day_terms)

stemmer = PorterStemmer()
#===============================================================================

# FEATURE EXTRACTION
def last_bigram(words):
    return {'__prev2__'+str(words[-2:]): 1}

def last_trigram(words):
    return {'__prev3__'+str(words[-3:]): 1}

def last_4gram(words):
    return {'__prev4__'+str(words[-4:]): 1}

def last_bigram_stem(words):
    stems = [stemmer.stem(w) for w in words]
    return {'__prev2_stem__'+str(stems[-2:]): 1}

def last_trigram_stem(words):
    stems = [stemmer.stem(w) for w in words]
    return {'__prev3_stem__'+str(stems[-3:]): 1}

def last_4gram_stem(words):
    stems = [stemmer.stem(w) for w in words]
    return {'__prev4_stem__'+str(stems[-4:]): 1}

def last_bigram_tags(words):
    bigram = words[-2:]
    pos_tags = [tag for (word, tag) in nltk.pos_tag(bigram)]
    return {str(pos_tags): 0}

def token_feat(words):
    lower_tok = words[-1].lower()
    return {'__token__'+str(lower_tok): 1}

def stem_feat(words):
    stem = stemmer.stem(words[-1]).lower()
    return {'__stem__'+str(stem): 1}

def tag_feat(words):
    tok = words[-1]
    tag = nltk.pos_tag([tok])[0][1]
    return {'__tag__'+str(tag): 1}

def tag_feat_stem(words):
    tok = words[-1]
    tag = nltk.pos_tag([tok])[0][1]
    return {'__tag_stem__'+str(tag[0]): 1}

def in_stopwords(words):
    lower_tok = words[-1].lower()
    if lower_tok in stopwords:
        return {'__stopword__':1}
    else:
        return {'__stopword__':0}

def in_stopwords_last(words):
    lower_tok = words[-2].lower()
    if lower_tok in stopwords:
        return {'__stopword_last__':1}
    else:
        return {'__stopword_last__':0}
    
def title_case(words):
    tok = words[-1]
    if tok.istitle() and tok != 'I':
        return {'__titlecase__': 1}
    else:
        return {'__titlecase__': 0}

def first_word(words):
    prev = words[:-1]
    if prev == ['<START>']:
        return {'__firstword__': 1}
    else:
        return {'__firstword__': 0}

def word_position(words):
    return {'__word_position__': len(words) - 1}


def all_numbers(words):
    tok = words[-1]
    if re.match(r'[0-9]+', tok):
        return {'__number__': 1}
    else:
        return {'__number__': 0}

def len_greater_2(words):
    tok = words[-1]
    if len(tok) > 2:
        return {'__len_>_2__': 1}
    else:
        return {'__len_>_2__': 0}

def len_greater_2_last(words):
    tok = words[-2]
    if len(tok) > 2:
        return {'__len_>_2_last__': 1}
    else:
        return {'__len_>_2_last__': 0}

def len_greater_3(words):
    tok = words[-1]
    if len(tok) > 3:
        return {'__len_>_3__': 1}
    else:
        return {'__len_>_3__': 0}

def go_to_at_in_3(words):
    prev = words[:-1]
    if re.search(r'(go(ing|ne)? +to)|at', ' '.join(prev[-3:]), re.I):
        return {'__go_to__': 1}
    else:
        return {'__go_to__': 0}

def how_about_in_5(words):
    prev = words[:-1]
    if re.search(r'how about', ' '.join(prev[-5:]), re.I):
        return {'__how_about__': 1}
    else:
        return {'__how_about__': 1}

def noun_tag(words):
    tok = words[-1]
    pos_tag = nltk.pos_tag([tok])[0][1]
    if pos_tag.startswith('N'):
        return {'__NOUN__': 1}
    else:
        return {'__NOUN__': 0}

def prop_noun_tag(words):
    tok = words[-1]
    pos_tag = nltk.pos_tag([tok])[0][1]
    if pos_tag == 'NNP':
        return {'__NNP__': 1}
    else:
        return {'__NNP__': 0}

def last_tag(words):
    prev_tok = words[-2]
    pos_tag = nltk.pos_tag([prev_tok])[0][1]
    return {'__PREV__'+pos_tag: 1}

def last_prep_tag(words):
    prev_tok = words[-2]
    pos_tag = nltk.pos_tag([prev_tok])[0][1]
    if pos_tag.startswith('P'):
        return {'__PREV_PREP__': 1}
    else:
        return {'__PREV_PREP__': 0}

def sent_tags(words):
    tags = [tag for (word, tag) in nltk.pos_tag(words)]
    return {str(tags): 1}

#FEATURE EXTRACTORS
def sounds_good(words):
    """does email contain phrase 'sounds good'?"""
    text = ' '.join(words)
    if re.findall('sounds good.', text):
        return {'_sg_': 1}
    else:
        return {'_sg_': 0}

def see_you(words):
    """does email contain phrase 'sounds good'?"""
    text = ' '.join(words)
    if re.findall('see you at|in|on .', text):
        return {'_sy_': 1}
    else:
        return {'_sy_': 0}

def word_location_feats(words):
    """1 if word is in doc; 0 otherwise"""
    words = set(words)
    return dict([(w, i) for i, w in enumerate(words)])
    
def bag_of_words_feats(words):
    """count(word) if word in doc; 0 otherwise"""
    fd = nltk.FreqDist(words)
    return dict([(w, fd.get(w, 0)) for w in words])

def set_of_words_feats(words):
    """1 if word is in doc; 0 otherwise"""
    words = set(words)
    return dict([(w, 1) for w in words])


def bag_tf(words):
    fdist = {}
    for word in words:
        word = word.lower()
        fdist[word] = fdist.get(word, 0) + 1
    return fdist

def bigrams_tf(words):
    fdist = {}
    for i, word in enumerate(words):
        if i == 0:
            continue
        fdist[words[i-1].lower() + word.lower()] = fdist.get(words[i-1].lower() + word.lower(), 0) + 1
    return fdist

def bigram_feats(words, score_fn=BigramAssocMeasures.chi_sq, n=300):
    '''take top n bigrams in email, not in training set'''
    words = [w.lower() for w in words]
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])

def bigram_feats_stem(words, score_fn=BigramAssocMeasures.chi_sq, n=500):
    stems = [stemmer.stem(w) for w in words]
    return bigram_feats(stems, score_fn, n)

def trigram_feats(words, score_fn=TrigramAssocMeasures.chi_sq, n=200):
    """"takes too long, use bigrams"""    
    words = [w.lower() for w in words]
    trigram_finder = TrigramCollocationFinder.from_words(words)
    trigrams = trigram_finder.nbest(score_fn, n)
    return dict([(ngram, True) for ngram in itertools.chain(words, trigrams)])

def trigram_feats_stem(words, score_fn=TrigramAssocMeasures.chi_sq, n=200):
    stems = [stemmer.stem(w) for w in words]
    return trigram_feats(stems, score_fn, n)

def bigram_time_terms(words):
    dict = {}
    prev = '__START__'
    for word in words:
        if word.lower() in all_terms:
            dict[prev + ' ' + word.lower()] = 1
    return dict    

def get_time_numbers(words):
    text = ' '.join(words)
    matches = re.findall('(\d+:\d+)|(\d* ?am|pm)',text)
    return {'nTimes': 1}

def get_nday_terms(words):
    c = 0
    for word in words:
        if word.lower() in day_terms:
            c += 1
    return {'nDayTerms': c}

def get_month_terms(words):
    c = 0
    for word in words:
        if word.lower() in month_terms:
            c += 1
    return {'nMonthTerms': c}

def generic_time_terms(words):
    c = 0
    for word in words:
        if word.lower() in time_terms:
            c += 1
    return {'nTimeTerms': c}

def word_shapes(words):
    feats = {}
    for word in words:
        if re.match(r'[0-9]+', word):
            feats['numOnly'] = feats.get('numOnly', 0) + 1
        if re.match(r'[A-Z][a-z]+', word):
            feats['titleCase'] = feats.get('titleCase', 0) + 1
        if re.match(r'[0-9]{1,2}\:[0-9]{1,2}', word):
            feats['timeEx'] = feats.get('timEx', 0) + 1
        elif re.search(r'(\.|\:|\?|\!|\)|\(|,|\/|\:|\;|\'|@)[^$]', word):
            feats['hasPunct'] = feats.get('hasPunct', 0) + 1
    return feats

def sentence_feats(words):
    text = ' '.join(words)
    return dict([(sent, 1) for sent in nltk.sent_tokenize(text)])

def sentence_feats_stem(words):
    text = ' '.join([stemmer.stem(w) for w in words])
    return dict([(sent, 1) for sent in nltk.sent_tokenize(text)])

def top_bigram_feats_stem(words, bigrams):
    '''take top n bigrams in training set that appear in email'''
    stems = [stemmer.stem(w) for w in words]
    return dict([(ngram, True) for ngram in itertools.chain(stems, set(bigrams))])

def top_set_of_words_feats(words, top_words):
    """1 if word is in doc; 0 otherwise"""
    words = set(words)
    return dict([(w, 1) for w in words if w in set(top_words)])

#===============================================================================
def get_fsets(feat_extractors, words, label, model_info={}):
    """Takes a feature extraction function, and a corpus reader,
    and returns training and test featuresets"""
    feature_dict = {}
    for f in feat_extractors:
        #if you need data from full training set, use it
        if str(f.__name__) in model_info.keys():
            features = dict( [(str(key), value) for (key, value) in f( words, model_info[f.__name__] ).iteritems()] )            
        #else, run feature on words alone
        else:
            features = dict( [(str(key), value) for (key, value) in f(words).iteritems()] )            
        feature_dict.update(features)
    return feature_dict

def get_model_info(instances, n_bigrams=100, n_unigrams=5000):
    '''gather information about training set overall: top bigrams, top unigrams, etc.'''
    #get all body text
    body_list = [body for (key, (body, subject, label)) in instances]
    body_text = ' __break__ '.join(body_list).lower()
    body_words = nltk.word_tokenize(body_text)
    #get all subject text
    sub_list = [subject for (key, (body, subject, label)) in instances]
    sub_text = ' __break__ '.join(sub_list).lower()
    sub_words = nltk.word_tokenize(sub_text)   
    #bigrams
    words = [stemmer.stem(w) for w in body_words + sub_words]
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, n_bigrams)
    #top words
    all_words = nltk.FreqDist()
    for w in body_words:
        if w not in stopwords:
            all_words.inc(w)
    top_words = all_words.keys()[:5000]
    return bigrams, top_words    
#===============================================================================

#DISCARDED
def utterance_length(words):
    '''precision down'''
    return {'__ut_length__':len(words)}

def bigram_tags(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    '''too slow?'''
    words = [w[1] for w in nltk.pos_tag(words)]
    #print words
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])

if __name__ == '__main__':
    test = [('1', ('dinner this Thursday?', 'reminder', 'yes')),
            ('2', ('check out our new hats!', 'reminder', 'no')),
            ('5', ('There will be a meeting this weekend', 'reminder', 'yes'))]
        
    #test
    #get_words('../../typeDectation')
    words = nltk.word_tokenize("see you at 2am Bob")
    print get_time_numbers(words)
