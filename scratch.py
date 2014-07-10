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
        
def all_false_check(path):
    with open(path, 'r') as fo:
        d = json.load(fo)        
        for key in sorted(d.keys()):
            venues = d[key]['html']['response']['venues']
            trigger = 0
            for v in venues:
                if v['correct'] == True:
                    trigger = 1
                    
            if trigger != 1:
                print key
                
def multiple_true_check(path, yes_threshold):
    with open(path, 'r') as fo:
        d = json.load(fo)        
        for key in sorted(d.keys()):
            venues = d[key]['html']['response']['venues']
            trigger = 0
            #print key
            for v in venues:
                if v['correct'] == True:
                    trigger += 1
                    
            if trigger > yes_threshold:
                print key
                
                
def add_data(old_path, new_path):
    '''load data from new_path json file into old_path json file'''
    final_data = {}
    i = 0
    with open(old_path, 'r') as old:
        old_data = json.load(old)
        for key in sorted(old_data.keys()):
            final_data[i] = old_data[key]
            i += 1
        old.close()
    with open(new_path, 'r') as new:
        new_data = json.load(new)
        new.close()
        for key in sorted(new_data.keys()):
            final_data[i] = new_data[key]
            i += 1
        new.close()    
    with open(old_path, 'w') as fw:
        json.dump(final_data, fw, indent=4, sort_keys=True)


if __name__ == '__main__':

    path = 'data/test_140710.json'
    data = json.load(open(path, 'r'))
    json.dump(data, open(path, 'w'), indent=4, sort_keys=True)

    
    #===========================================================================
    # path = 'data/data_new.json'  
    # with open(path, 'r') as old:
    #     old_data = json.load(old)
    #     for k in sorted(old_data.keys()):
    #         print k
    #         x = old_data[k]['lat']
    #===========================================================================
    #add_data('data/data_new.json', 'data/tmp.json')

    #all_false_check(path)
    #multiple_true_check(path, 2)

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
    
    #===========================================================================
    # path = 'data/data_new.json'
    # with open(path, 'r') as fo:
    #     data = json.load(fo)
    #     old = []
    #     for key in sorted(data.keys()):
    #         if data[key]['sent'] not in old:
    #             print data[key]['sent']
    #             print
    #             old.append(data[key]['sent'])
    #===========================================================================
            
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






