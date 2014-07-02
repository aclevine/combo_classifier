### README

#### WORD TAGGING
Given utterance, select words that are venues

run typeDetector/run_classifier.py on data dictionary to produce:
- venue classification metrics
- data to test on 4square search classification.

	python typeDetector/run_classifier.py --corpus <path to json> 
		i.e.: python ./typeDetector/run_classifier.py --corpus ./data/data_new.json


use "-- randomize" argument to randomly select test from records (but possibly lose novelty)

		i.e.: python ./typeDetector/run_classifier.py --corpus ./data/data_new.json --randomize

#### Results
#####  Venue Prediction
###### 2014-06-1 : 15989 test items (pieces of ~1000 sentences, stopping at candidate word)

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


#### 4-SQUARE SEARCH RESULT TAGGING
Given venue keywords, select which result returned by 4square is the desired venue

run typeDetector/run_classifier.py using "--type fsq" argument to run 4-square result classification on the provided corpus set.

	python typeDetector/run_classifier.py --corpus <path to json> --type fsq
		i.e.: python ./typeDetector/run_classifier.py --corpus ./data/data_new.json --type fsq

use "-- randomize" argument to randomly select test from records (but possibly lose novelty)

		i.e.: python ./typeDetector/run_classifier.py --corpus ./data/data_new.json --type fsq --randomize


#### Results
#####  Search Prediction
###### 2014-06-2 : 4797 test items (search result from ~1000 sentences with ~1-3 venues a piece)

	    yes   no    
	yes 223.0 39.0  
	no  109.0 589.0 

	========= Yes =========
	Precision: 0.851145 
	Recall: 0.671687
	F-measure 0.750842
	========= No =========
	Precision: 0.843840 
	Recall: 0.937898
	F-measure 0.888386

	Accuracy: 84.583333%
	
Features:
	is_first_result,
	result_rank,
	result_count


	- is query exact match for returned venue name?
	- number of overlapping tokens between query and returned venue name
	- does utterance have overlapping tokens with returned venue location data
	- is the returned venue a restaurant
	- Did 4square deem result the most relevant? (first result?)
	- How relevant did 4square deem the returned venue

