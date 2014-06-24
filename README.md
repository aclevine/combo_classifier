### README


Requires compiled copy of liblinear-1.94 in comboclassifier directory

#### VENUE
Given utterance, select words that are venues

run classify_venue.py on data to produce:
- venue classification metrics
- data to test on 4square search classification under venueresults.json


#### Results
#####  Venue Prediction
###### 2014-05-19
-Precision: 0.875000
-Recall: 0.870892
-F1: 0.872941

- Features:
	- Ignore first two tokens in each sentence 
	- Previous 3 tokens ~ 63.19
	- Length of target token > 2 ~ 69.94
	- Shape of first 3 chars of target token (fire only if length>2) ~ 73.01
		- Title case, all numbers, time formats
	- First 3 chars of target token in stopword list ~ 75.46
	- 'go(ing|ne)? to' or 'at' occurs in previous 3 tokens ~ 77.91
	- 'how about' occurs in previous 5 tokens ~ 78.53
	- 'place(s)?' occurs anywhere in previous tokens ~ 79.14
	- 'down for' occurs in previous 5 tokens ~ 79.75
	- Target token all caps ~ 80.37



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
	