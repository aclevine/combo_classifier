### README

#### WORD TAGGING
Given utterance, select words that are venues

run typeDetector/run_classifier.py on data dictionary to produce:
- venue classification metrics
- data to test on 4square search classification.

	python typeDetector/run_classifier.py --corpus <path to json> 
		i.e.: python ./typeDetector/run_classifier.py --corpus ./data/data_new.json


#### Results
#####  Venue Prediction
###### 2014-06-1 : 15989 test bits (pieces of ~1000 sentences, stopping at candidate word)

    yes   no     
yes 428.0 77.0   
no  83.0  2610.0 

========= Yes =========
Precision: 0.847525 
Recall: 0.837573
F-measure 0.842520
========= No =========
Precision: 0.969179 
Recall: 0.971344
F-measure 0.970260

Accuracy: 94.996873%

features:
                    last_bigram_stem,
                    last_trigram_stem,
                    title_case,
                    bigram_feats_stem,
                    sentence_feats,
                    token_feat,
                    len_greater_2,
                    go_to_at_in_3,
                    sentence_feats_stem,
                    stem_feat,
                    last_4gram_stem,
                    in_stopwords,
                    last_tag,
                    tag_feat,
                    last_bigram,
                    first_word


#### SEARCH 
Given venue keywords, select which result returned by 4square is the desired venue

run venue_to_search.py to convert venueresults.json to searchresults.json, for testing on search classifier
run searchclassifier.py to get search results classification metrics

#### Results
#####  Search Prediction
###### 2014-05-19
-Precision: 0.825503
-Recall: 0.831081
-F1: 0.828283

-Features
	- is query exact match for returned venue name?
	- number of overlapping tokens between query and returned venue name
	- does utterance have overlapping tokens with returned venue location data
	- is the returned venue a restaurant
	- Did 4square deem result the most relevant? (first result?)
	- How relevant did 4square deem the returned venue
	
	
#### ROC graph functionality
compile a copy of liblinear from the python directory.  place files in liblinear-roc.  Do not overwrite plotroc.py.
	