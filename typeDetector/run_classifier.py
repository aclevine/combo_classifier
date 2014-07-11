#!/usr/bin/env python
'''
Created on May 19, 2014

@author: aclevine
'''
import argparse
from datetime import datetime
import os
import random
import re
import sys

from sklearn.linear_model import LogisticRegression 
#from sklearn.decomposition import TruncatedSVD

from corpus import *
from feature_extract import *
from SKClassifier import SKClassifier

def write_results():
    pass

def write_set(instances, training=False):
    path = '%s_%d.txt' % (get_timestamp(), len(instances))
    if training:
        if not os.path.exists('./tdTrain'):
            os.mkdir('./tdTrain')
        path = os.path.join('./tdTrain', path)
    else:
        if not os.path.exists('./tdTest'):
            os.mkdir('./tdTest')
        path = os.path.join('./tdTest', path)
    with open(path, 'w') as fo:
        for instance in instances:
            fo.write("%s\n" % instance[0])

def write_hyp(outfile, pred, instances):
    with open(outfile, 'w') as fo:
        for i, p in enumerate(pred):
            if p != instances[i][1][2]:
                fo.write("Pred:%s Act:%s\t%s\n" % (p, instances[i][1][2],instances[i][0]))

def read_paths_file(file):
    with open(file) as fo:
        threads = []
        yes = 0
        no = 0
        for line in fo:
            if line.strip() != '':
                yield line.strip()
                if re.findall('/yes/', line):
                    yes += 1
                if re.findall('/no/', line):
                    no += 1
                threads.append(re.sub('/no/', '/yes/', os.path.split(line)[0]))
    print '## yes emails: %d, no emails: %d, total emails: %d' % (yes, no, yes+no)
    print '## total threads: %d' % len(set(threads))

def load_corpus(path):
    corpus = {}
    for label in os.listdir(path):
        if label.startswith('.'):
            continue
        corpus[label.strip('/')] = Corpus(os.path.join(path, label))
    return corpus

def create_instances_body(corpus):
    instances = {}
    labels = set()
    for label in corpus:
        labels.add(label)
        for fid in corpus[label].fileids:
            instances[fid] = (corpus[label].get_body(fid), corpus[label].get_subject(fid), label)
    return (instances, labels)

def read_template(path):
    features = []
    with open(path) as fo:
        for line in fo:
            if line.startswith('#'):
                continue
            features.append(globals()[line.strip()])
    return features

def get_timestamp():
    now = datetime.today()
    return now.strftime("%y%m%d")

def word_classify(args):
    ## BUILD CLASSIFIER
    features = []
    if args.template is None:
        features = [
                    last_bigram_stem,
                    last_trigram_stem,
                    title_case,
                    bigram_feats_stem,
                    token_feat,
                    len_greater_2,
                    sentence_feats,
                    sentence_feats_stem,
                    stem_feat,
                    last_4gram_stem,
                    in_stopwords,
                    last_tag,
                    tag_feat,
                    first_word,
                    in_stopwords_last,
                    go_to_at_in_3,
                    last_bigram,
                    last_4gram,
                    last_trigram,
                    #len_greater_3,

                    ]
    else:
        features = read_template(args.template)
    clf = SKClassifier(LogisticRegression(), features)
    print "# Reading corpus at %s..." % args.corpus
    c = Corpus(args.corpus) ## LOAD INSTANCES
    labels = ['yes', 'no']
    print "# Found %d labels: " % len(labels)
    print "#\t" + str(labels)
    clf.add_labels(labels)
    
    train_data = []
    test_data = []
    if args.test_file:
        test_c = Corpus(args.test_file)
        test_data = test_c.word_instances
        
    if test_data == []:
        instances = c.word_instances
        if args.randomize:
            random.shuffle(instances)
        split = int(len(instances) * args.split)
        train_data = instances[:split]
        test_data = instances[split:]
    else:
        train_data = c.word_instances
    
    print "# Training on %d instances..." % len(train_data),
    ## TRAIN
    clf.train(train_data)
    # TEST
    if test_data != []:
        pred = clf.classify(test_data)
        clf.evaluate(pred, [label(x) for x in test_data])


def fsq_classify(args):
    ## BUILD CLASSIFIER
    features = []
    if args.template is None:
        features = [
                    is_first_result,
                    result_count,
                    result_rank,
                    lat_long_dist,
                    name_edit_dist#,
                    #===========================================================
                    # is_restaurant,
                    # any_token_match
                    #===========================================================
                    ]
    else:
        features = read_template(args.template)
    clf = SKClassifier(LogisticRegression(), features)
    print "# Reading corpus at %s..." % args.corpus
    c = Corpus(args.corpus) ## LOAD INSTANCES
    labels = ['yes', 'no']
    print "# Found %d labels: " % len(labels)
    print "#\t" + str(labels)
    clf.add_labels(labels)
    
    train_data = []
    test_data = []
    if args.test_file:
        test_c = Corpus(args.test_file)
        test_data = test_c.fsq_instances
        
    if test_data == []:
        instances = c.fsq_instances
        if args.randomize:
            random.shuffle(instances)
        split = int(len(instances) * args.split)
        train_data = instances[:split]
        test_data = instances[split:]
    else:
        train_data = c.fsq_instances
    
    print "# Training on %d instances..." % len(train_data),
    ## TRAIN
    clf.train(train_data)
    # TEST
    if test_data != []:
        pred = clf.classify(test_data)
        clf.evaluate(pred, [label(x) for x in test_data])


def combo_classify(args):
    ## WORD STAGE
    features = []
    if args.template is None:
        features = [
                    last_bigram_stem,
                    last_trigram_stem,
                    title_case,
                    bigram_feats_stem,
                    token_feat,
                    len_greater_2,
                    sentence_feats,
                    sentence_feats_stem,
                    stem_feat,
                    last_4gram_stem,
                    in_stopwords,
                    last_tag,
                    tag_feat,
                    first_word,
                    in_stopwords_last,
                    go_to_at_in_3,
                    last_bigram,
                    last_4gram,
                    last_trigram
                    ]
    else:
        features = read_template(args.template)
    clf = SKClassifier(LogisticRegression(), features)
    print "# Reading corpus at %s..." % args.corpus
    c = Corpus(args.corpus) ## LOAD INSTANCES
    labels = ['yes', 'no']
    print "# Found %d labels: " % len(labels)
    print "#\t" + str(labels)
    clf.add_labels(labels)
    
    train_data = []
    test_data = []
    if args.test_file:
        test_c = Corpus(args.test_file)
        test_data = test_c.combo_instances
        
    if test_data == []:
        instances = c.combo_instances
        if args.randomize:
            random.shuffle(instances)
        split = int(len(instances) * args.split)
        train_data = instances[:split]
        test_data = instances[split:]
    else:
        train_data = c.combo_instances
    
    print "# Training on %d instances..." % len(train_data),
    ## TRAIN
    clf.train(train_data)
    # TEST
    if test_data != []:
        pred = clf.classify(test_data)
        if args.verbose:
            print "## word -> venue tagging"
            clf.evaluate(pred, [label(x) for x in test_data])

    ## FSQ STAGE
    features = []
    if args.template is None:
        feat_fsq = [
                    is_first_result,
                    result_count,
                    result_rank,
                    lat_long_dist,
                    name_edit_dist,
                    name_exact_match,
                    any_token_match,
                    is_restaurant,
                    is_coffee,
                    any_token_match,
                    location_token_match
                    ]
    else:
        feat_fsq = read_template(args.template)
    clf_fsq = SKClassifier(LogisticRegression(), feat_fsq)
    print "# Reading corpus at %s..." % args.corpus
    c = Corpus(args.corpus) ## LOAD INSTANCES
    labels = ['yes', 'no']
    print "# Found %d labels: " % len(labels)
    print "#\t" + str(labels)
    clf_fsq.add_labels(labels)
    
    train_data_fsq = [(inst[3], inst[1], inst[4]) for inst in train_data]
    test_data_fsq = [(inst[3], inst[1], inst[4]) for inst in test_data]
     
    print "# Training on %d instances..." % len(train_data),
    ## TRAIN
    clf_fsq.train(train_data_fsq)
    # TEST
    pred_fsq = clf_fsq.classify(test_data_fsq)     
    if args.verbose:
        print "## search result -> correct tagging"
        clf_fsq.evaluate(pred_fsq, [label(x) for x in test_data_fsq])

    # COMBO STAGE
    pred_final = []
    for i in range(len(pred)):
        if pred[i] == 'yes':
            pred_final.append(pred_fsq[i])
        else:
            pred_final.append(pred[i])           
    
    print "## combo tagging"
    clf_fsq.evaluate(pred_final, [label(x) for x in test_data_fsq])
         
    

def classify_from_console():
    ''' parse arguments from console, 
    send arguments off to word_classify, fsq_classify or combo_classify as needed'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True, 
                        help="Corpus where files for testing and/or training can be found.")
    parser.add_argument('--template', help="Path to template file specifying features.")
    parser.add_argument('--model', help="Where to save/find the model. If file already exists, model will be loaded.\
                                        If no path is given, no model will be saved.")
    parser.add_argument('--train-file', help="Path to file with testing paths")
    parser.add_argument('--test-file', help="Path to file with testing paths")
    parser.add_argument('--split', type=float, default=0.8, help="Float indicating how much to use for training.\
                                                            Default is 0.8. Set to 0 to only test, and 1 to only train.")
    parser.add_argument('--hyp-file', default='hypSKClf.txt', help="Where to save hypothesis file.")

    parser.add_argument('--recall-boost', type=float, default=0, 
                        help="number between 0 and 1. 0 has lowest recall/highest precision,\
                                1 has highest recall/lowest precision")

    parser.add_argument('--precision-boost', type=float, default=0, 
                        help="number between 0 and 1. 0 has lowest precision/highest recall,\
                                1 has highest precision/lowest recall")
    parser.add_argument('--randomize', action='store_true', 
                        help="If included, randomly select test and training set. Otherwise, just take in order (novel data)")        
    parser.add_argument('--verbose', action='store_true', 
                        help="If included, display results of word and 4-square steps of combo classification")        
    parser.add_argument('--type', default='word', 
                        help="word = test classifying words as venues\
                            fsq = test classifying 4-square search results as matches or not\
                            combo = classify word, than classify search results from word")
            
    args = parser.parse_args()
    
    if args.type == 'word':
        word_classify(args)
    if args.type == 'fsq':
        fsq_classify(args)
    if args.type == 'combo':
        combo_classify(args)
    

def label(inst):
    return inst[0]

def token(inst):
    return inst[1]

def prev_tokens(inst):
    return inst[2]

def featurize_test():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True, 
                        help="Corpus where files for testing and/or training can be found.")
    args = parser.parse_args()
    c = Corpus(args.corpus)
    feat_extractors = [utterance_length]
    for inst in c.word_instances:
        body = prev_tokens(inst) + [token(inst)]
        print get_fsets(feat_extractors, body, label(inst))

if __name__ == '__main__':
    classify_from_console()
    