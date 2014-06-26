'''
Created on May 14, 2014

@author: aclevine
'''
#=============================================================================== 
from __future__ import print_function
import glob
import os
from subprocess import check_call
from searchhelper import build_features
#===============================================================================


def run_crossfold(n, ofn=False):
    '''use ~n% of data for test, train liblinear model on rest.
    return metrics for the model (precision/recall/F1/etc.'''
    
    lines = []

    fp = 0
    tp = 0
    fn = 0
    tn = 0

    with open('search_data.svm') as fo:
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

        check_call(['../liblinear-1.94/train', '-s', '5', 'crstemptrain.txt', 'crstemp.model'])
        check_call(['../liblinear-1.94/predict', 'crstemptest.txt', 'crstemp.model', 'crstempout.txt'])

        predicted = []
        with open('crstempout.txt') as fo:
            for line in fo:
                predicted.append(line.strip())

        for i, item in enumerate(test):
            if predicted[i].startswith('-1'):
                if item.startswith('-1'):
                    tn += 1
                else:
                    fn += 1
                    #===========================================================
                    # if ofn:
                    #     print("False Negative:", file=ofile)
                    #     print(item.split('|\t|')[1], file=ofile)
                    #     print("\n", file=ofile)
                    #===========================================================
            elif predicted[i].startswith('1'):
                if item.startswith('+1'):
                    tp += 1
                else:
                    fp += 1
                    if ofn:
                        print("False Positive:", file=ofile)
                        print(item.split('|\t|')[1], file=ofile)
                        print("\n", file=ofile)
                        
    if ofn:
        ofile.close()
    p = float(tp) / (tp + fp)
    r = float(tp) / (tp + fn)
    f = p * r / (p + r) * 2
    print("\nResults:")
    print("\tPrecision: %f" % p)
    print("\tRecall: %f" % r)
    print("\tF1: %f" % f)

    print("\nTrue positive: %d" % tp)
    print("False negative: %d" % fn)
    print("False positive: %d" % fp)


def run_full_crossfold(n, ofn=False):
    
    lines = []
    alt = []

    fp = 0
    tp = 0
    fn = 0
    tn = 0

    with open('search_data.svm') as fo:
        for line in fo:
            lines.append(line.strip())
    
    with open('test_data.svm') as fo:
        for line in fo:
            alt.append(line.strip())
            
    tenth = len(lines) / n
    #random.shuffle(lines)
    if ofn:
        ofile = open(ofn, 'w')
    for x in xrange(n):
        start = x * tenth
        #test = lines[start:start+tenth]
        train = lines[:start] + lines[start+tenth:]

        with open('crstemptrain.txt', 'w') as fo:
            out_train = []
            for item in train:
                out_train.append(item.split("|\t|")[0])
            fo.write('\n'.join(out_train))
            del out_train
            
        with open('crstemptest.txt', 'w') as fo:
            out_test = []
            for item in alt:
                out_test.append(item.split("|\t|")[0])
            fo.write('\n'.join(out_test))
            del out_test
            
        check_call(['../liblinear-1.94/train', '-s', '5', 'crstemptrain.txt', 'crstemp.model'])
        check_call(['../liblinear-1.94/predict', 'crstemptest.txt', 'crstemp.model', 'crstempout.txt'])

        predicted = []
        with open('crstempout.txt') as fo:
            for line in fo:
                predicted.append(line.strip())

        for i, item in enumerate(alt):
            if predicted[i].startswith('-1'):
                if item.startswith('-1'):
                    tn += 1
                else:
                    fn += 1
                    #===========================================================
                    # if ofn:
                    #     print("False Negative:", file=ofile)
                    #     print(item.split('|\t|')[1], file=ofile)
                    #     print("\n", file=ofile)
                    #===========================================================
            elif predicted[i].startswith('1'):
                if item.startswith('+1'):
                    tp += 1
                else:
                    fp += 1
                    if ofn:
                        print("False Positive:", file=ofile)
                        print(item.split('|\t|')[1], file=ofile)
                        print("\n", file=ofile)
 
    if ofn:
        ofile.close()
    p = float(tp) / (tp + fp)
    r = float(tp) / (tp + fn)
    f = p * r / (p + r) * 2
    print("\nResults:")
    print("\tPrecision: %f" % p)
    print("\tRecall: %f" % r)
    print("\tF1: %f" % f)
 
    print("\nTrue positive: %d" % tp)
    print("False negative: %d" % fn)
    print("False positive: %d" % fp)



if __name__ == '__main__':
    #pull features from test data
    build_features('../data/test.json', 'search_data.svm')
    build_features('../data/search_results.json', 'test_data.svm')


    #subdivide feature vectors, train model, test model, get metrics
    run_full_crossfold(10)

    #ROC curve data
    check_call(['python', '../liblinear-roc/python/plotroc.py', '-T', 'crstemptest.txt', '-s', '4', 'crstemptrain.txt'])
