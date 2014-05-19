'''
Created on May 16, 2014

@author: aclevine
'''
import re
import json 
import urllib


def rebuild_venue_sents(path):
    '''get back data from 4 square search classifier to run on text classifier'''
    #load data json
    data = json.load(open(path, 'r'))
    #send sentence field to text 
    f = open('data/venue_sentences.txt', 'w')    
    f.write('')
    f = open('data/venue_sentences.txt', 'a')    
    last = ''
    for key in data.keys():
        if data[key]['sent'] != last:
            f.write(data[key]['sent'] + '\n')
            last = data[key]['sent'] 

    
def search(venue, lat, lon):
    '''use json from extract_venues() to send queries to four square
    add results to json entries under 'html' key'''
    identity = 'jamie+testb@pencil.ai'
    auth = 'CAAFdcNYDjcUBAEGXpgn5XAHE8iURKVg60Vq'
    location = '&ll='+ lat +','+lon #location = '&ll=42.3581,-71.0636' #Boston, MA

    query = venue.lower()
    query_url = 'http://' + identity + ':' + auth + '@staging.wyth.com/api/v1/venues/searchNatural?q=' + query + location
    response = urllib.urlopen(query_url)
    html = json.loads(response.read()) #check
    #move to json
    return html


def select_venue(data, venue_results, key):
    '''if multiple venues, which one do we want to test on?'''
    for venue in venue_results[key]:
        search = ''
        toks = re.sub("'", "", venue).split()
        name_toks = data[key]['venueName']
        
        for t in toks:
            if t in name_toks:
                return venue
                
  
def venue_results_search():
    '''send out 4square requests based on venue classifier results'''
    data = json.load(open('data/test_new.json', 'r'))
    venue_results = json.load(open('data/venue_results.json', 'r'))
    
    search_results = {}    
    for key in set(venue_results.keys()):
        search_results[key] = {}
        venue = select_venue(data, venue_results, key)
        if venue != None:
            search_results[key]['venueName'] = venue
            search_results[key]['html']= search(search_results[key]['venueName'] , '42.3581','-71.0636')          
            search_results[key]['sent'] = data[key]['sent']
        else:
            search_results[key]['venueName'] = venue_results[key]
            search_results[key]['html']= {"request":{"status":"ok","timing":{"request_complete":"109ms"}},"response":{"venues":[],"count":0}}       
            search_results[key]['sent'] =  data[key]['sent']

    with open('search_results.json', 'w') as fo:
        json.dump(search_results, fo, indent=4, sort_keys=True)
        

def tag_test_data():
    '''assign true / false markers to venues in test data'''
    data = json.load(open('data/test_new.json', 'r'))
    search_results = json.load(open('search_results.json', 'r'))
 
    for key in set(search_results.keys()):
        result = search_results[key]
        if result['html']['response']['count'] == 0:
            result['html']['response']['venues'] = {'correct': False}

        else:
            check_list = data[key]['html']['response']['venues']
            venues = result['html']['response']['venues']
            for v in venues:
                for c in check_list:
                    if v['name'] == c.get('name', None):
                        v['correct'] = c['correct']
                        break
                    else:
                        v['correct'] = False
                        
    with open('search_results.json', 'w') as fo:
        json.dump(search_results, fo, indent=4, sort_keys=True)
                

def main():
    venue_results_search()
    tag_test_data()


if __name__ == '__main__':
    main()