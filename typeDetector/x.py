'''
Created on Jun 30, 2014

@author: aclevine
'''
import json
import re
import nltk
from subprocess import check_call

#===============================================================================
# HELPER FUNCTIONS 
stopwords = nltk.corpus.stopwords.words('english')

def new_to_old_tags(sent):
    '''convert to old tagging method'''
    old_sent = re.sub('<..?>', '', sent)
    venues = re.findall('<v>(.+?)</v>', sent)
    for v in venues:
        toks = v.split()
        tagged_v = '|venue '.join(toks) + '|venue '
        old_sent = re.sub(v, tagged_v, old_sent)
    return old_sent
#===============================================================================

class Corpus(object):
    def __init__(self, cdir):
        self.doc_path = cdir
        self.sents = []
        self.test_data = []
        self.feat_func = []
        
        self.load_sents()
        self.load_test_data()

    def load_sents(self):
        '''load sentences from dictionary into corpus object'''
        data = json.load(open(self.doc_path, 'r'))
        instances = []
        for key in data.keys():
            sent = data[key]['sent']
            self.sents.append(sent)

    def load_test_data(self):
        '''convert sentences into basic token features for additional feature extraction and testing'''
        test_sents = set(self.sents) #remove duplicates
        for sent in test_sents:
            old_sent = new_to_old_tags(sent)
            tokens = nltk.word_tokenize(old_sent) 
            previous = ['<START>']            
            for tok in tokens:
                tag = 0
                if tok.endswith('|venue'):
                    tag = 1
                    tok = re.sub(r'\|venue', '', tok)            
                self.test_data.append( (tag, tok, previous) )
                previous = previous + [tok]
                
    def load_feat_func(self, functions):
        if type(functions) is list:
            self.feat_func = functions
        else:
            raise "error: require functions in list format"

#===============================================================================

# FEATURE EXTRACT
# inst = (label, token, previous tokens)
def label(inst):
    return inst[0]

def token(inst):
    return inst[1]

def prev_token_list(inst):
    return inst[2]

# FEATURE EXTRACTION
def last_bigram(inst):
    prev = prev_token_list(inst)
    feat = {'__prev2__'+str(prev[-2:]): 1}
    return feat

def last_trigram(inst):
    prev = prev_token_list(inst)
    feat = {'__prev3__'+str(prev[-3:]): 1}
    return feat

def token_feat(inst):
    tok = token(inst)
    lower_tok = tok.lower()
    feat = {'__token__'+str(lower_tok): 1}
    return feat

def in_stopwords(inst):
    tok = token(inst)
    if tok in stopwords:
        return {'__stopword__':1}

def title_case(inst):
    tok = token(inst)
    if tok.istitle() and tok != 'I':
        return {'__titlecase__': 1}

def first_word(inst):
    prev = prev_token_list(inst)
    if prev == ['<START>']:
        return {'__firstword__': 1}

def all_numbers(inst):
    tok = token(inst)
    if re.match(r'[0-9]+', tok):
        return {'__number__': 1}

def len_greater_2(inst):
    tok = token(inst)
    if len(tok) > 2:
        return {'__len_>_2__': 1}

def go_to_at_in_3(inst):
    prev = prev_token_list(inst)
    if re.search(r'(go(ing|ne)? +to)|at', ' '.join(prev[-3:]), re.I):
        return {'__go_to__': 1}

def how_about_in_5(inst):
    prev = prev_token_list(inst)
    if re.search(r'how about', ' '.join(prev[-5:]), re.I):
        return {'__how_about__': 1}

def noun_tag(inst):
    tok = token(inst)
    pos_tag = nltk.pos_tag(tok)
    if pos_tag.startswith('N'):
        return {'__NOUN__': 1}

def prop_noun_tag(inst):
    tok = token(inst)
    pos_tag = nltk.pos_tag(tok)
    if pos_tag == 'NNP':
        return {'__NNP__': 1}


if __name__ == '__main__':
    # TEST
    d = {
        "html": {
            "request": {
                "status": "ok", 
                "timing": {
                    "request_complete": "132ms"
                }
            }, 
            "response": {
                "count": 4, 
                "venues": [
                    {
                        "correct": True, 
                        "dateCreated": 1403706707832, 
                        "dateModified": 1403706707832, 
                        "kind": "Foursquare", 
                        "location": {
                            "address": "135 Richmond St", 
                            "city": "Boston", 
                            "country": "United States", 
                            "crossStreet": "at North St.", 
                            "lat": 42.36314198849343, 
                            "lng": -71.05414152145386, 
                            "postalCode": "02109", 
                            "state": "MA"
                        }, 
                        "name": "Mare Oyster Bar", 
                        "primaryCategory": {
                            "icon": "https://ss1.4sqi.net/img/categories_v2/food/seafood_{icon_size}.png", 
                            "id": "4bf58dd8d48988d1ce941735", 
                            "name": "Seafood Restaurant"
                        }, 
                        "sourceId": "4a1b3a1cf964a520d97a1fe3", 
                        "url": ""
                    }, 
                    {
                        "correct": False, 
                        "dateCreated": 1403706707833, 
                        "dateModified": 1403706707833, 
                        "kind": "Foursquare", 
                        "location": {
                            "address": "7 Blue Hill River Rd", 
                            "city": "Canton", 
                            "country": "United States", 
                            "crossStreet": "", 
                            "lat": 42.20581132381635, 
                            "lng": -71.11915564231984, 
                            "postalCode": "02021", 
                            "state": "MA"
                        }, 
                        "name": "Maresfield Farm", 
                        "primaryCategory": {
                            "icon": "https://ss1.4sqi.net/img/categories_v2/building/default_{icon_size}.png", 
                            "id": "4bf58dd8d48988d124941735", 
                            "name": "Office"
                        }, 
                        "sourceId": "4b4b298bf964a520739326e3", 
                        "url": ""
                    }, 
                    {
                        "correct": False, 
                        "dateCreated": 1403706707835, 
                        "dateModified": 1403706707835, 
                        "kind": "Foursquare", 
                        "location": {
                            "address": "99 Salem St", 
                            "city": "Boston", 
                            "country": "United States", 
                            "crossStreet": "btwn Cross & Parmenter", 
                            "lat": 42.36396642595342, 
                            "lng": -71.05566447147389, 
                            "postalCode": "02113", 
                            "state": "MA"
                        }, 
                        "name": "Mercato del Mare (North End Fish Market)", 
                        "primaryCategory": {
                            "icon": "https://ss1.4sqi.net/img/categories_v2/shops/food_fishmarket_{icon_size}.png", 
                            "id": "4bf58dd8d48988d10e951735", 
                            "name": "Fish Market"
                        }, 
                        "sourceId": "4b95883df964a520dba734e3", 
                        "url": ""
                    }, 
                    {
                        "correct": False, 
                        "dateCreated": 1403706707836, 
                        "dateModified": 1403706707836, 
                        "kind": "Foursquare", 
                        "location": {
                            "address": "265 Nantasket Ave", 
                            "city": "Hull", 
                            "country": "United States", 
                            "crossStreet": "at Hull Shore Dr.", 
                            "lat": 42.27217015277616, 
                            "lng": -70.85888554511303, 
                            "postalCode": "02045", 
                            "state": "MA"
                        }, 
                        "name": "Mezzo Mare", 
                        "primaryCategory": {
                            "icon": "https://ss1.4sqi.net/img/categories_v2/food/italian_{icon_size}.png", 
                            "id": "4bf58dd8d48988d110941735", 
                            "name": "Italian Restaurant"
                        }, 
                        "sourceId": "4b642965f964a520e6a12ae3", 
                        "url": ""
                    }
                ]
            }
        }, 
        "lat": 42.3581, 
        "long": -71.0636, 
        "sent": "Italian Seafood ... <v>Daily Catch</v>. <v>Mare</v>.", 
        "venueName": "Mare"
    }
    
    venues = d['html']['response']['venues']
    
    request = d['venueName']
    fsq_results = d['html']['response']['venues']
    sent_data = d['sent'].split('<v>'+request+'</v>')[0] + request    
    sent_data = re.sub('</?v>', '', sent_data)
    
    print sent_data
        
    
    
    
    #===========================================================================
    # c = Corpus('../data/data_new.json')
    # for inst in c.test_data:
    #     print first_word(inst)
    #===========================================================================
    
    #===========================================================================
    # words = ['I','am','the','night']
    # 
    # toks = words[:len(words)]
    # print toks
    #===========================================================================