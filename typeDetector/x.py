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
    #===========================================================================
    # c = Corpus('../data/data_new.json')
    # for inst in c.test_data:
    #     print first_word(inst)
    #===========================================================================
    
    words = ['I','am','the','night']
    
    toks = words[-2:]
    print toks