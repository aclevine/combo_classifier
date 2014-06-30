'''
Created on May 17, 2014

@author: aclevine
'''
import nltk
import re
import pprint
import json
import urllib

def venue_count():
    with open('data/venue_sentences.txt', 'r') as fo:
        text = fo.read()
        venues = re.findall('<v>.+?</v>', text)
        print len(venues)

def sentence_to_dict(input, output):
    pp = pprint.PrettyPrinter(indent=4)
    with open('data/venue_sentences.txt', 'r') as fo:
        text = fo.read()
        sents = text.split('\n\n')
        #print sents
        i = 0
        t_dict = {}
        for s in sents:
            venues = re.findall('<v>(.+?)</v>', s)
            for v in venues:
                t_dict[str(i)] = {'venue':v, 'sent':s}
                i += 1
        pp.pprint(t_dict) 
        
        
        
if __name__ == '__main__':
    #===========================================================================
    # path = 'data/data_new.json'
    # with open(path, 'r') as fo:
    #     text = fo.read()
    #     i = 0
    #     while i < 990:
    #         if len( re.findall('"'+str(i)+'": {', text) ) == 0:
    #             print i
    #             print re.findall('"'+str(i)+'": {', text)
    #             i += 1
    # 
    #===========================================================================
    
    path = 'data/data_new.json'
    with open(path, 'r') as fo:
        data = json.load(fo)
        #=======================================================================
        # old = []
        # for key in sorted(data.keys()):
        #     if data[key]['sent'] not in old:
        #         print data[key]['sent']
        #         print
        #         old.append(data[key]['sent'])
        #=======================================================================
            
    #===========================================================================
    # path = 'data/data_new.json'
    # with open(path, 'r') as fo:
    #     data = json.load(fo)
    #     new= {}
    #     i = 0
    #     for key, value in data.iteritems():
    #         new[i] = value
    #         i += 1
    #         print i
    # json.dump(new, open('data/test.json', 'w'), indent=4, sort_keys=True)
    #===========================================================================
 
     

#===============================================================================
#     identity = 'jamie+testb@pencil.ai'
#     auth = 'CAAFdcNYDjcUBAEGXpgn5XAHE8iURKVg60Vq'
#     location = '&ll=42.3581,-71.0636' #Boston, MA
# 
#     venue = 'sagra'
#     query = 'http://' + identity + ':' + auth + '@staging.wyth.com/api/v1/venues/searchNatural?q=' + venue + location
#     response = urllib.urlopen(query)
#     html = response.read()
#     print json.loads(html)
#     print type(json.loads(html))
#     #move to json
#===============================================================================
        
    #===========================================================================
    # with open('data/venue_sentences.txt', 'r') as fo:
    #     text = fo.read().decode('utf-8')
    #     clean_text = re.sub('<..?>', '', text)
    #     sents_new = clean_text.split('\n\n')
    #     #print sents
    #     fo.close()
    # 
    # with open('data/data_new.json', 'r') as fo:
    #     v_dict = json.load(fo)
    #     for key in v_dict.keys():
    #         if re.sub('\|venue', '', v_dict[key]['sent']) not in sents_new:
    #             print re.sub('\|venue', '', v_dict[key]['sent'])
    #             print '\n'
    #===========================================================================

             
#build data

#input: sentence with tagged data

# 1) read sentence


# 2) find venue in sentence
    # save numbers for rating
    
# 3) take venue, send to 4-square
    # save numbers for rating
    
# 4) return performance data on system 


#===============================================================================
# path = 'pants.json'
# #extract_search_data(path, '42.3581', '-71.0636')
# 
# data = json.load(open(path, 'r+'))
# for key in data.keys():
#     print type(json.loads(data[key]['html']))
#===============================================================================






