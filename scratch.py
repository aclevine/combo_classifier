'''
Created on May 17, 2014

@author: aclevine
'''
from get_data import *


path = 'pants.json'
#extract_search_data(path, '42.3581', '-71.0636')

data = json.load(open(path, 'r+'))
for key in data.keys():
    print type(json.loads(data[key]['html']))
