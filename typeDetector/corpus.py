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
        # load test data
        self.doc_path = cdir
        self.dict_data = json.load(open(self.doc_path, 'r'))               
        
        # convert data for specific word / four square classification testing
        self.word_instances = []
        self.fsq_instances = []
        self.load_word_test_data()
        self.load_fsq_test_data()

    def load_word_test_data(self):
        '''convert sentences into basic token features for additional feature extraction and testing'''        
        # build sentence set
        test_sents = set([self.dict_data[key]['sent'].encode('utf-8') for key in self.dict_data.keys()]) #remove duplicates
        # divide into instances
        for sent in test_sents:
            old_sent = new_to_old_tags(sent)
            tokens = nltk.word_tokenize(old_sent) 
            previous = ['<START>']            
            for tok in tokens:
                tag = 'no'
                if tok.endswith('|venue'):
                    tag = 'yes'
                    tok = re.sub(r'\|venue', '', tok)            
                self.word_instances.append( (tag, tok, previous + [tok]) )
                previous = previous + [tok]
                
    def load_fsq_test_data(self):
        for key in self.dict_data.keys():
            # PARSE DATA
            d = self.dict_data[key]
            venueName = d['venueName']
            fsq_results = d['html']['response']['venues']
            sent_data = d['sent'].split('<v>'+venueName+'</v>')[0] + venueName #limit sentence to tokens before search was performed
            sent_data = re.sub('</?v>', '', sent_data)
            # BUILD TEST INSTANCES
            for idx, v in enumerate(fsq_results):
                # format data
                body = {'sent':sent_data, 'result_rank':idx+1, 'result': v, 
                        'count': d['html']['response']['count'], 'venueName': venueName,
                        'lat':d['lat'],'long':d['long']}
                if v['correct']:
                    label = 'yes'
                else:
                    label = 'no'
                # load instance into object
                inst = (label, venueName, body) #inst =  (tag, tok, body)
                self.fsq_instances.append(inst)


if __name__ == '__main__':
    #TESTING
    c = Corpus('../data/data_new.json')
    print len(c.fsq_instances)
    for inst in c.fsq_instances:
        print inst
