Subjectivity-Classifier
=======================

A tool that classifies NYTimes articles as subjective or objective. 
The final project for Professor Kauchak's CS159 (Natural Language Processing) class at Pomona College

Project Overview
----------------

We use the New York Times API to create a corpus of articles from general news and the op-ed section. 
We access the api in article_urls.py and then scrape NYT in create_corpus.py

We then use SVM Light to classify our data. The bulk of the work happens in run_svm.py, where we create our svm files,
train our model, and then test our model on 10% of our data.




