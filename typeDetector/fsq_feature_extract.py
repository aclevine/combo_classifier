'''
Created on May 14, 2014

@author: aclevine

feature extractor to determine if we should return a venue
have:
    -venue name
    -utterance
    -json returned by 4square

for each venue, want
    -how many other venues were returned?
    -does venue name match name in utterance? (account for fuzzy search)
    -does locational data in utterance match any data in location or name for 
'''
#===============================================================================
import json
import math
import nltk
import re
from string import punctuation
from subprocess import check_call
#===============================================================================

stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
                'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
                'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
                'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
                'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
                'between', 'into', 'through', 'during', 'before', 'after', 'above',
                'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
                'over', 'under', 'again', 'further', 'then', 'once', 'here',
                'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
                'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

#===============================================================================
# PULL MULTIPLE FEATURES
def get_fsets(feat_extractors, body, label, model_info={}):
    """Takes a feature extraction function, and a corpus reader,
    and returns training and test featuresets"""
    feature_dict = {}
    for f in feat_extractors:
        #if you need data from full training set, use it
        if str(f.__name__) in model_info.keys():
            features = dict( [(str(key), value) for (key, value) in f( body, model_info[f.__name__] ).iteritems()] )            
        #else, run feature on words alone
        else:
            features = dict( [(str(key), value) for (key, value) in f(body).iteritems()] )            
        feature_dict.update(features)
    return feature_dict
#===============================================================================


# FEATURE EXTRACTORS
def result_count(body):
    '''how many results did we get back from 4square?'''
    return {"__result_count__": body["count"]}
    
def name_exact_match(body):
    venue_name = body['result']['name']
    if venue_name ==  body['request']:
        return {'__name_match__': 1}
    else:
        return {'__name_match__': 0}


def name_token_match(body):
    '''how many tokens in venue name are also in result?
    not weighting this by length right now, but may be worth a look'''    
    # load tokens
    request_tokens = [v for v in body['request'].split() if v not in stopwords]
    venue_name_tokens = [v for v in body['result']['name'].split() if v not in stopwords]
    # get token overlap counts
    overlap_count = len([t for t in request_tokens if t in venue_name_tokens])

    return {'__name_ovlp__': overlap_count}


def location_token_match(body):
    '''how many tokens in utterance are also in venue location?
    not weighting this by length right now, but may be worth a look'''
    #clean location data
    loc_data = [v for v in body['results']['location'].values() if type(v) == 'unicode']
    loc_string = ' '.join(loc_data)
    loc_tokens = set([t for t in nltk.word_tokenize(loc_string) if t not in stopwords])
    #clean sent
    sent_tokens = set([t for t in nltk.word_tokenize(body['sent']) if t not in stopwords])

    return {'__loc_ovlp__': len([t for t in sent_tokens if t in loc_tokens])}


def lat_long_dist(body):
    '''4square provides specific gps location data for each venue'''
    my_lat = body['lat']
    my_lng = body['long']
    location = body['result']['location']
    x = my_lat - location['lat']
    y = my_lng - location['lng']
    return {'__ll_dist__': round( math.sqrt( x * x + y * y), 3) } #euclidean distance between provided location and venue


def is_first_result(body):
    '''is returned item top result?'''
    if body['result_rank'] == 1:
        return {'__top_rslt__': 1}
    else:
        return {'__top_rslt__': 0}
#===============================================================================


if __name__ == "__main__":
    ## TEST
    test = [{"lat": 42.3581, "long": -71.0636, 'count': 20, 'request': u'Brookline Fire Station 7', 'result': {u'primaryCategory': {u'id': u'4bf58dd8d48988d12c941735', u'name': u'Fire Station', u'icon': u'https://ss1.4sqi.net/img/categories_v2/building/government_firestation_{icon_size}.png'}, u'kind': u'Foursquare', u'name': u'Brookline Fire Station 7', u'sourceId': u'4dc76ad6315170a4221a8c86', u'correct': False, u'url': u'', u'location': {u'city': u'Brookline', u'country': u'United States', u'postalCode': u'02446', u'state': u'MA', u'crossStreet': u'', u'address': u'665 Washington St', u'lat': 42.33874747861062, u'lng': -71.13341236183228}, u'dateCreated': 1404139484228, u'dateModified': 1404139484228}, 'sent': u'Game at Fenway after lunch, dinner in Brookline', 'result_rank': 19},
            {"lat": 42.3581, "long": -71.0636, 'count': 20, 'request': u'Brookline', 'result': {u'primaryCategory': {u'id': u'4bf58dd8d48988d1e6941735', u'name': u'Golf Course', u'icon': u'https://ss1.4sqi.net/img/categories_v2/parks_outdoors/golfcourse_{icon_size}.png'}, u'kind': u'Foursquare', u'name': u'Brookline Country Club', u'sourceId': u'4bca28a0b6c49c74b5ea8f91', u'correct': False, u'url': u'', u'location': {u'city': u'Chestnut Hill', u'country': u'United States', u'postalCode': u'02467', u'state': u'MA', u'crossStreet': u'', u'address': u'', u'lat': 42.310473508717955, u'lng': -71.14271928193887}, u'dateCreated': 1404139484229, u'dateModified': 1404139484229}, 'sent': u'Game at Fenway after lunch, dinner in Brookline', 'result_rank': 20},
            {"lat": 42.3581, "long": -71.0636, 'count': 4, 'request': u'ATO', 'result': {u'primaryCategory': {u'id': u'4bf58dd8d48988d1b0941735', u'name': u'Fraternity House', u'icon': u'https://ss1.4sqi.net/img/categories_v2/education/frathouse_{icon_size}.png'}, u'kind': u'Foursquare', u'name': u'ATO, Tufts University', u'sourceId': u'4aff19c4f964a520343422e3', u'correct': True, u'url': u'', u'location': {u'city': u'Medford', u'country': u'United States', u'postalCode': u'02155', u'state': u'MA', u'crossStreet': u'Curtis', u'address': u'134 Professors Row', u'lat': 42.407488160327205, u'lng': -71.12427592277527}, u'dateCreated': 1404139497366, u'dateModified': 1404139497366}, 'sent': u'There will be a mandatory meeting tonight at ATO', 'result_rank': 1}]

    for t in test:
        print name_exact_match(t)
        print name_token_match(t)
        print lat_long_dist(t)
        print is_first_result(t)