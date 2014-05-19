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
# TARGET
def classifiable(venue):
    try:
        if venue['correct']:
            return '+1'
        else:
            return '-1'
    except:
        return '-1'
#===============================================================================    
# FEATURES
def result_count(search_result):
    '''how many results did we get back from 4square?'''
    return search_result['response']['count']
    
def name_exact_match(venue_name, venue):
    if venue_name.lower() == venue['name'].lower(): #fairly brittle
        return 1
    else:
        return 0

def name_token_match(venue_name, venue):
    '''how many tokens in venue name are also in result?
    not weighting this by length right now, but may be worth a look'''
    user_name_tokens = [v for v in venue_name.split() if v not in stopwords]
    search_name_tokens = [v for v in venue['name'].split() if v not in stopwords]
    
    return len([t for t in user_name_tokens if t in search_name_tokens])


def location_token_match(utterance, venue):
    '''how many tokens in utterance are also in venue location?
    not weighting this by length right now, but may be worth a look'''
    #clean location data
    loc_string = ' '.join([s for s in venue['location'].values() if type(s) == 'unicode']).lower()  + venue['name'].lower() # remove lat long data

    loc_tokens = set([t for t in loc_string.split() if t not in stopwords])
    #clean utterance
    ut = re.sub('\|venue', '', utterance)
    for p in punctuation:
        ut = re.sub( '\\' + p, '', ut).lower()
    ut_tokens = set([t for t in ut.split() if t not in stopwords])
    
    return len([t for t in ut_tokens if t in loc_tokens])


def lat_long_dist(lat, long, venue):
    '''4square provides specific gps location data for each venue'''
    location = venue['location']
    x = lat - location['lat']
    y = long - location['lng']
    return math.sqrt( x * x + y * y) #euclidean distance between provided location and venue


def is_first_result(venue, venue_list):
    '''is returned item top result?'''
    if venue == venue_list[0]:
        return 1
    else:
        return 0

# should use search results to build backwards index, be able to classify type based on terms
foodwords = set(['dinner', 'lunch', 'eat', 'breakfast', 'bite', 'reservation',
                 'burger', 'mexican', 'try'])

def food_venue(utterance):
    ut = re.sub('\|venue', '', utterance)
    for p in punctuation:
        ut = re.sub( '\\' + p, '', ut).lower()
    ut_tokens = set([t for t in ut.split() if t not in stopwords]) 
    
    if len(ut_tokens & foodwords) != 0:
        return 'Restaurant'
    else:
        return ''
    
def is_type(venue, venue_type):
    if venue.has_key('primaryCategory' ) and venue_type in venue['primaryCategory']['name'].split():
        return 1
    else:
        return 0
#===============================================================================
# FULL FEATURE EXTRACTOR
def build_features(inpath, outpath):
    '''load test data, extract desired feature sets,
    export to test file'''
    test = json.load(open(inpath, 'r'))
    f = open(outpath, 'w')
    f.write('')
    f = open(outpath, 'a')

    for key in test.keys():
        #load available data
        data = test[key]
        venue_name = data["venueName"]
        utterance = data["sent"]
        search_result = data["html"]
        #pull features
        venue_list = search_result['response']['venues']        
        i = 1
        for venue in venue_list:
            features = []
            features.append(classifiable(venue))
            features.append('1:' + str(- result_count(search_result)))
            if result_count(search_result) != 0:
                features.append('2:' + str(name_exact_match(venue_name, venue)))    
                features.append('3:' + str(name_token_match(venue_name, venue)))   
                features.append('4:' + str(location_token_match(utterance, venue)))
                features.append('5:' + str(is_type(venue, 'Restaurant'))) #weight specific venue (Restaurants, etc.) more than others
                
                features.append('6:' + str(is_first_result(venue, venue_list))) #weigh top result heavily
                features.append('7:' + str(i)) #weight later results less and less

                i += 1
            f.write(' '.join(features) + "|\t|" + venue_name + '\n')



if __name__ == "__main__":
    #test: feature extraction working?
    path = 'data/test_new.json'
    build_features(path)
