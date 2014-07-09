'''
Created on May 13, 2014

@author: aclevine
'''
import re
import urllib
import json

# MAIN FUNCTIONS
def extract_venue_data(sent_path, data_path, i=0):
    '''grab venue names from venue_sentences, send venue and origin sentence 
    to json keyed on sentence number'''
    #setup json dict
    data = {}
    with open(sent_path, 'r') as fo:
        #divide sentences
        text = fo.read()
        sents = text.split('\n\n')
        for s in sents:
            #pull out venues
            venues = re.findall('<v>(.+?)</v>', s)
            for v in venues:
                #send venues and sentences to json dict
                data[str(i)] = {'venueName':v, 'sent':s}
                i += 1        
        json.dump(data, open(data_path, 'w'), indent=4)


def extract_4sq_data(data_path, lat, long):
    '''use json from extract_venues() to send queries to four square
    add results to json entries under 'html' key'''
    identity = 'jamie+testb@pencil.ai'
    auth = 'CAAFdcNYDjcUBAEGXpgn5XAHE8iURKVg60Vq'
    location = '&ll='+ lat +','+long #location = '&ll=42.3581,-71.0636' #Boston, MA
    
    with open(path, 'r') as fo:
        data = json.load(fo)
        for key in data.keys():
            #send requests to 4 square
            venue = data[key]['venueName'].lower().decode('utf-8', 'ignore')
            venue = clean_venue(venue) 
            query = 'http://' + identity + ':' + auth + '@staging.wyth.com/api/v1/venues/searchNatural?q=' + venue + location
            try:
                response = urllib.urlopen(query)            
                html_text = response.read()
                html_dict = json.loads(html_text) 
                #move to json
                data[key]['html'] = html_dict
            except:
                continue
        json.dump(data, open(path, 'w'), indent=4, sort_keys=True)

def clean_venue(text):
    clean_text = re.sub("'s", "s", text) # 's not being parsed by 4square API 
    clean_text = re.sub("and|&", "", clean_text) # and not being screened out by API
    #clean_text = re.sub("s$", "", clean_text)

    return clean_text


# HELPER FUNCTIONS FOR HUMAN TAGGING    
def pull_ambiguous_data(inpath, outpath):
    '''use json returned by search() method, select all cases which returned
    2 or more json hits, send to ambigous.json for human annotation'''
    data = json.load(open(inpath, 'r'))        
    test = {}

    for key in data.keys():        
        result_count = data[key]['html']['response']['count']        
        #skip results with no returns
        if result_count >= 2: 
            test[key] = data[key]

    json.dump(test, open(outpath, 'w'), indent=4, sort_keys=True)


def get_testable_data(inpath, outpath):
    '''find all examples that could be disambiguated by human, send to test.json for testing'''
    test = json.load(open(inpath, 'r')) 
    testable_data = {}
    for key in test.keys():
        venues = test[key]['html']['response']['venues']
        
        for v in venues:
            if len(re.findall('\|good', v['name'])) > 0:
                testable_data[key] = test[key]

    json.dump(testable_data, open(outpath, 'w'), indent=4, sort_keys=True)


def add_new_data(old_path, additional_path, new_path):

    old = json.load(open( old_path , 'r'))    
    add = json.load(open( additional_path , 'r'))
    #build new json
    new = {}    
    i = 1
    for key in old.keys():
        new[i] = old[key]
        i += 1
    for key in add.keys():
        new[i] = add[key]
        i += 1
    json.dump(new, open( new_path, 'w'), indent=4, sort_keys=True)


if __name__ == "__main__":

    path = 'data/tmp.json'   
    extract_venue_data('data/tmp.txt', path, 0) 
    extract_4sq_data(path, '42.3581', '-71.0636')

    #add = json.load(open( path , 'r'))
    #json.dump(add, open( path, 'w'), indent=4, sort_keys=True)
    #add_new_data('data/test_old.json', 'data/data_new.json', 'data/test_new.json')