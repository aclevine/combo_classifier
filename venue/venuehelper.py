import codecs
import json
import re
import sys

from nltk import pos_tag
import nltk

stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
                'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
                'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
                'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
                'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
                'between', 'into', 'through', 'during', 'before', 'after', 'above',
                'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
                'over', 'under', 'again', 'further', 'then', 'once', 'here',
                'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
                'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

lf = ['t)', 'rack', '20th', 'tuk?!']


# FEATURE FUNCTIONS
def in_stopwords(tok, previous_tokens):
    if len(tok) > 3:
        tok = tok[:3]
    if tok.lower() in stopwords:
        return True
    return False

def title_case(tok, previous_tokens):
    if len(tok) > 3:
        tok = tok[:3]
    if re.match(r'[A-Z][a-z]+', tok):
        return True
    return False

def all_numbers(tok, previous_tokens):
    if len(tok) > 3:
        tok = tok[:3]
    if re.match(r'[0-9]+', tok):
        return True
    return False

def time_ex1(tok, previous_tokens):
    if len(tok) > 3:
        tok = tok[:3]
    if re.match(r'[0-9]{1,2}\:[0-9]?', tok):
        return True
    return False

def time_ex2(tok, previous_tokens):
    if len(tok) > 3:
        tok = tok[:3]
    if re.match(r'[0-9]+(p|a)m?', tok, re.I):
        return True
    return False

def len_greater_2(tok, previous_tokens):
    if len(tok) > 2:
        return True
    return False

def go_to_at_in_3(tok, previous_tokens):
    if re.search(r'(go(ing|ne)? +to)|at', ' '.join(previous_tokens[-3:]), re.I):
        return True
    return False

def how_about_in_5(tok, previous_tokens):
    if re.search(r'how about', ' '.join(previous_tokens[-5:]), re.I):
        return True
    return False

def previous_the(tok, previous_tokens):
    if re.search(r'\s+the\s+', ' '.join(previous_tokens[-4:]), re.I):
        return True
    return False

def places_in_sentence(tok, previous_tokens):
    if re.search(r'\s+places?\s+', ' '.join(previous_tokens), re.I):
        return True
    return False

def down_for(tok, previous_tokens):
    if re.search(r'\s+down for?\s+', ' '.join(previous_tokens[-5:]), re.I):
        return True
    return False

def all_caps(tok, previous_tokens):
    if len(tok) > 3:
        tok = tok[:3]
    if re.match(r'[A-Z]+$', tok):
        return True
    return False

def prep_in_last(tok, previous_tokens):
    tags = set(tag for word, tag in pos_tag(previous_tokens)[-4:])
    if 'TO' in tags or 'IN' in tags:
        return True
    else:
        return False

def noun_tag(tok, previous_tokens):
    if pos_tag([tok])[0][1].startswith('N'):
        return True
    else:
        return False

def prop_noun_tag(tok, previous_tokens):
    if pos_tag([tok])[0][1] == 'NNP':
        return True
    else:
        return False

def the_in_last(tok, previous_tokens):
    words = set(word for word in previous_tokens[-2:])
    if 'the' in words:
        return True
    else:
        return False
 
def prev_trigram(tok, previous_tokens):
    tok = ["<START_0>", "<START_1>"] + previous_tokens
    
    
def prev_3_letters(tok, previous_tokens):
    #Reduces recall ~9, increases precision ~13
    prev = previous_tokens[-1].lower()
    print prev
    print prev[-3:]
    if prev not in lf:
        return features[prev[-3:]]

def test(tok, previous_tokens):
    return


def convert_to_svm(string, index):
    #These features will always fire
    always_fire_ff = [prop_noun_tag, noun_tag, len_greater_2, go_to_at_in_3, places_in_sentence, all_caps, prep_in_last, prev_3_letters]
    #These features will only fire if length of current token > 2
    len_cond_fire_ff = [in_stopwords, title_case, all_numbers, time_ex1, time_ex2]
    
    s = string
    #Store feature indices
    global features
    features = {'<start_0>':1, '<start_1>':2, '<start_2>':3}
    fic = 3
    for item in always_fire_ff:
        if item.__name__ not in features:
            fic += 1
            features[item.__name__] = fic

    for item in len_cond_fire_ff:
        if item.__name__ not in features:
            fic += 1
            features[item.__name__] = fic

    p = ''
    prev = ''
    toks = nltk.word_tokenize(s) #toks = s.split()
    for tok in toks:
        tok = re.sub(r'\|venue', '', tok.lower())
        if tok in lf:
            tok = "<UNK>"
        elif tok[-3:] not in features:
            fic += 1
            features[tok[-3:]] = fic
        if tok not in features:
            fic += 1
            features[tok] = fic
        p = tok

    # Featurize
    instances = []
    previous_tokens = []
    toks = nltk.word_tokenize(s) #toks = s.split()
    prev3 = ["<START_0>", "<START_1>"]
    
    for tok in toks:
        label = 0
        if re.search(r'\|venue', tok):
            label = 1
        tok = re.sub(r'\|venue', '', tok)
    
        # We only check for venues after first two tokens.
        if len(prev3) >= 2:
            istring = str(label)
            f_id = set(features["<UNK>"] if i in lf else features[i.lower()] for i in prev3)
            
            # These features will always fire
            for func in always_fire_ff:
                if func(tok, previous_tokens):
                    f_id.add(features[func.__name__])
            
            # These features only fire if the length of the current token is
            # greater than 2.
            if len(tok) > 2:
                for func in len_cond_fire_ff:
                    if func(tok, previous_tokens):
                        f_id.add(features[func.__name__])
                        
            # Convert features to SVM format.
            f_id = list(f_id)
            istring += ' '
            istring += ' '.join(['%d:1' % i for i in sorted(f_id)])
            istring += "|\t|Current: %s\tTokens: %s\tIndex:%s" % (tok, ' '.join(previous_tokens), index)
            instances.append(istring)
            
            prev3.pop(0)
            
            
            
        previous_tokens.append(tok)
        prev3.append(tok.lower())
        
    with open('tempkey.json', 'w') as fw:
        jstring = json.dumps(features, sort_keys=True, indent=4)
        fw.write(jstring)

    return instances


if __name__ == '__main__':
    #test
    d = {"lat": 42.3581, 
    "long": -71.0636, 
    "sent": "In the North End, try <v>La Summa</v>, <v>Cantina Italiana</v>, <v>Massimino's</v> or <v>Pizzeria Regina</v>.", 
    "venueName": "Cantina Italiana"}
    
    i_list = convert_to_svm('Staying at the Kimpton|venue downtown for a conference.', 1)
    for i in i_list:
        print i
