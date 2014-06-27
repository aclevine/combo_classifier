from __future__ import print_function
#===============================================================================
# import argparse
# import glob
# import os
# import random
#===============================================================================
import json
import re
import os
import glob
from subprocess import check_call
from venuehelper import convert_to_svm

def new_to_old_tags(sent):
    '''convert to old tagging method'''
    old_sent = re.sub('<..?>', '', sent)
    venues = re.findall('<v>(.+?)</v>', sent)
    for v in venues:
        toks = v.split()
        tagged_v = '|venue '.join(toks) + '|venue'
        old_sent = re.sub(v, tagged_v, old_sent)
    return old_sent
    
def load_venues(inpath):
    data = json.load(open(inpath, 'r'))
    instances = []
    for key in data.keys():
        #change data to one venue
        sent = data[key]['sent']
        venues = re.findall('<v>.+?</v>', sent)
        for v in venues:
            if v != '<v>'+data[key]['venueName']+'</v>':
                sent = re.sub(v,'VENUENAME',sent)
        sent = new_to_old_tags(sent)
        #load data
        feature_list = convert_to_svm(sent, key)
        instances.extend(feature_list)
        
    with open('../data/venue_data.svm', 'w') as fw:
        fw.write('\n'.join(instances).encode('utf-8', 'ignore'))

def run_crossfold(n, ofn=False):
    lines = []
    fp = 0
    tp = 0
    fn = 0
    tn = 0

    with open('../data/venue_data.svm') as fo:
        for line in fo:
            lines.append(line.strip())

    tenth = len(lines) / n
    #random.shuffle(lines)
    if ofn:
        ofile = open(ofn, 'w')
    for x in xrange(n):
        start = x * tenth
        test = lines[start:start+tenth]
        train = lines[:start] + lines[start+tenth:]

        with open('crstemptrain.txt', 'w') as fo:
            out_train = []
            for item in train:
                out_train.append(item.split("|\t|")[0])
            fo.write('\n'.join(out_train))
            del out_train
        with open('crstemptest.txt', 'w') as fo:
            out_test = []
            for item in test:
                out_test.append(item.split("|\t|")[0])
            fo.write('\n'.join(out_test))
            del out_test

        check_call(['../liblinear-1.94/train', '-s', '2', 'crstemptrain.txt', 'crstemp.model'])
        check_call(['../liblinear-1.94/predict', 'crstemptest.txt', 'crstemp.model', 'crstempout.txt'])

        predicted = []
        with open('crstempout.txt') as fo:
            for line in fo:
                predicted.append(line.strip())

        results_dict = {}
        keyword_list = []
        key = ''
        # get metrics
        for i, item in enumerate(test):
            if predicted[i].startswith('0'):
                if item.startswith('0'):
                    tn += 1
                else:
                    fn += 1
                    if ofn:
                        print("False Negative:", file=ofile)
                        print(item.split('|\t|')[1], file=ofile)
                        print("\n", file=ofile)
                if keyword_list != []:
                    if results_dict.has_key(key):
                        results_dict[key].append(' '.join(keyword_list))
                    else:
                        results_dict[key] = [' '.join(keyword_list)]
                    keyword_list = []
                    
            elif predicted[i].startswith('1'):
                if item.startswith('1'):
                    tp += 1
                    #if ofn:
                    #    print("True Positive:", file=ofile)
                    #    print(item.split('|\t|')[1], file=ofile)
                    #    print("\n", file=ofile)
                    #if extract:
                else:
                    fp += 1
                    #if ofn:
                    #    print("False Positive:", file=ofile)
                    #    print(item, file=ofile)
                    #    print("\n", file=ofile)
                #get data    
                result = item.split("|\t|")[1]
                keyword = re.findall("Current: (.*?)\t", result)[0]
                key = re.findall("Index\:(\d+)", result)[0]
                keyword_list.append(keyword)
     
    if ofn:
        ofile.close()
    #display metrics
    p = float(tp) / (tp + fp)
    r = float(tp) / (tp + fn)
    f = p * r / (p + r) * 2
    print("\nResults:")
    print("\tPrecision: %f" % p)
    print("\tRecall: %f" % r)
    print("\tF1: %f" % f)

    print("\nTrue positive: %d" % tp)
    print("False negative: %d" % fn)
    
    #save results for next step
    json.dump(results_dict, open('../data/venue_results.json', 'w'), sort_keys=True, indent=4)


if __name__ == '__main__':

    load_venues('../data/data_new.json')

    run_crossfold(10)
    for f in glob.glob('crstemp*'):
        if f.endswith('model'):
            continue
        os.remove(f)
