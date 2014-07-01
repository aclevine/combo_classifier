import re
import json
import nltk

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
        self.instances = []
        
        self.load_sents()
        self.load_test_data()

    def load_sents(self):
        '''load sentences from dictionary into corpus object'''
        data = json.load(open(self.doc_path, 'r'))
        for key in data.keys():
            sent = data[key]['sent'].encode('utf-8')
            self.sents.append(sent)

    def load_test_data(self):
        '''convert sentences into basic token features for additional feature extraction and testing'''
        test_sents = set(self.sents) #remove duplicates
        for sent in test_sents:
            old_sent = new_to_old_tags(sent)
            tokens = nltk.word_tokenize(old_sent) 
            previous = ['<START>']            
            for tok in tokens:
                tag = 'no'
                if tok.endswith('|venue'):
                    tag = 'yes'
                    tok = re.sub(r'\|venue', '', tok)            
                self.instances.append( (tag, tok, previous) )
                previous = previous + [tok]

    #inst =  (tag, tok, previous) 
    def label(self, inst):
        return inst[0]
    
    def token(self, inst):
        return inst[1]
    
    def pre_toks(self, inst):
        return inst[2]    