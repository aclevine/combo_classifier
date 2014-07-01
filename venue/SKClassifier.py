#!/usr/bin/env python
import json

from nltk import word_tokenize
import numpy as np
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer

from feature_extract import *
from util.alphabet import Alphabet
from util.evaluator import ConfusionMatrix
from gensim import corpora, models, similarities

class SKClassifier():
    def __init__(self, clf, ffuncs):
        self.feature_funcs = ffuncs
        self.clf = clf
        self.labels = Alphabet()
        self.features = DictVectorizer() 
        self.model_info = {} #keys = feature extractors; values = data for feature extractors
    
    def add_labels(self, labels):
        for label in labels:
            self.labels.add(label.decode('utf-8', 'ignore'))
            
    def featurize(self, instances, test=False):
        X = []
        y = []
        #instance = (path, (body, subject, label))
        #get features(instances, funcs to use, other data)
        #return: (X = [fDict1, fDict2, ...] , list of bigrams)
        if self.model_info == {} and (top_bigram_feats_stem or top_set_of_words_feats in self.feature_funcs):
            bigrams, top_words = get_model_info(instances)
            self.model_info['top_bigram_feats_stem'] = bigrams
            self.model_info['top_set_of_words_feats'] = top_words
        for idx, instance in enumerate(instances):
            try:
                y.append(self.labels.get_index(instance[1][2]))
            except KeyError:
                if not test:
                    print "Couldn't find %s in set of labels. ^C if this is a problem." % instance[1][2]
            feats = get_fsets(self.feature_funcs, word_tokenize(instance[1][0]), 'body', self.model_info)
            feats.update(get_fsets(self.feature_funcs, word_tokenize(instance[1][1]), 'sub', self.model_info))
            X.append(feats)
        if test:
            return (self.features.transform(X), y)
        else:
            return (self.features.fit_transform(X), y)
    
    
    def thread_evaluate(self, pred, actual):
        print "\n========= Thread Evaluation ========="
        act_threads = {}
        pred_threads = {}
        for idx, act in enumerate(actual):
            thrid = act[0].split('/')[-3]
            if thrid in act_threads:
                if act[1] == 'yes':
                    act_threads[thrid] = 'yes'
                if pred[idx] == 'yes':
                    pred_threads[thrid] = 'yes'
            else:
                act_threads[thrid] = act[1]
                pred_threads[thrid] = pred[idx]
        ep, ea = zip(*[(pred_threads[tid], act_threads[tid]) for tid in act_threads])
        self.evaluate(list(ep), list(ea))
                
    
    def load_model(self, path):
        self.clf = joblib.load(os.path.join(path, 'model.pkl'))
        with open(os.path.join(path, 'labels.json'), 'r') as fo:
            self.labels = Alphabet.from_dict(json.load(fo))
        with open(os.path.join(path, 'model_info.json'), 'r') as fo:
            self.model_info = json.load(fo)            
        self.features = joblib.load(os.path.join(path, 'featvec.pkl'))
    
    def save_model(self, path, testset, features):
        if not os.path.exists(path):
            os.makedirs(path)
        joblib.dump(self.clf, os.path.join(path, 'model.pkl'))
        with open(os.path.join(path, 'labels.json'), 'w') as fo:
            json.dump(self.labels.to_dict(), fo)
        with open(os.path.join(path, 'model_info.json'), 'w') as fo:
            json.dump(self.model_info, fo)
        joblib.dump(self.features, os.path.join(path, 'featvec.pkl'))
        #with open(os.path.join(path, 'testSet.txt'), 'w') as fo:
        #    fo.write('\n'.join([x[0] for x in testset]))
        with open(os.path.join(path, 'featureSet.txt'), 'w') as fo:
            fo.write('\n'.join([x.__name__ for x in features]))
