from collections import Counter
from nltk import RegexpParser, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
# from nltk.corpus import conll2000
import pandas as pd

import re
import html.parser
from .__settings import amazon_review_file_loc

"""
from assignment_solution.noun_phrase_summarizer import sandbox
sandbox()

from assignment_solution import noun_phrase_summarizer as nps
nps.clean_dataset()
"""

def clean_dataset():
	amazonReviewDF = pd.read_json(amazon_review_file_loc, lines=True)
	
	col_label = amazonReviewDF.columns.get_loc("reviewText") 
	url_regex = r"https?\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?"

	# print("before")
	# print(amazonReviewDF.iloc[1,2])
	count = 0
	for index, d in amazonReviewDF.iterrows():
		
		review = d.reviewText
		review_lower = review.lower()
		review_no_html_code = html.parser.unescape(review_lower)
		review_no_url = re.sub(url_regex, '<URL>', review_no_html_code)

		amazonReviewDF.iloc[count,col_label] = review_no_url
		count += 1
	# print('after')
	# print(amazonReviewDF.iloc[1,2])

	return amazonReviewDF

import math
import sys, os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import amazon_review_file_loc

def sandbox():
	tfidf_top_3()
 

def extract_top_20_from_reviews():
	amazonReviewDF = pd.read_json(amazon_review_file_loc, lines=True)
	c = Counter()
	for index, d in amazonReviewDF.iterrows():
		input_data = d.reviewText + " " + d.summary
		extract_np(c, input_data)
		if index%100 == 0:
			print("\rfinished %d iterations" %index, end="")
	
	print("\n {}".format(c.most_common(20)))

def top_3():
	amazonReviewDF = pd.read_json(amazon_review_file_loc, lines=True)
	pop_products = ['B005SUHPO6','B0042FV2SI','B008OHNZI0']
	for product in pop_products:
		c = Counter()
		
		df = amazonReviewDF.loc[amazonReviewDF.asin==product]
		for index, d in df.iterrows():
			input_data = d.reviewText + " " + d.summary
			extract_np(c, input_data)
		print("\n10 representative noun phrases for {} are: {}".format(product, c.most_common(10)))

def tfidf_top_3():
	amazonReviewDF = pd.read_json(amazon_review_file_loc, lines=True)
	np_to_products = dict()
	c = Counter()
	products = ['B005SUHPO6','B0042FV2SI','B008OHNZI0']
	for product in products:		
		df = amazonReviewDF.loc[amazonReviewDF.asin==product]
		for index, d in df.iterrows():
			extract_np(c, d.reviewText)
		for noun_phrase in set(c.elements()):
			try:
				np_to_products[noun_phrase] += 1
			except KeyError:
				np_to_products[noun_phrase] = 0

	for noun_phrase in c.elements():
		c[noun_phrase] = c[noun_phrase] * math.log(len(products)/1+np_to_products[noun_phrase])

	print(c.most_common(20))
"""
a.
1. tf-idf
2. remove repeated words

b. try training a classifier
"""

"""
for part 1: we want to have a slacker rule - NBAR: {<NN.*|JJ.*>*<NN.*>} NP: {<NBAR>} {<NBAR><IN><NBAR>}
for part 2: we want adjectives cause they are more representative
"""

def tfidf_extract_np(data):
	grammar = r"""
		NBAR: {<NN.*|JJ.*>+<NN.*>}
		NP: {<NBAR>}
			{<NBAR><IN><NBAR>}
	"""
	
	cp = RegexpParser(grammar)
	text = word_tokenize(data)
	sentence = pos_tag(text)
	result = []
	parsed_sentence = cp.parse(sentence)
	for np in clean_np(parsed_sentence):
		result.append(np)
	c = Counter()
	return c.update(lower_and_lemma(result))

def extract_np(c, data):
	#refine the grammar?
	# grammar = r"""
	#     NP: {<PDT|DT>+<JJ|JJR|JJS>+<NN|NNS|NNP|NNPS>+}
	#         # {<NN|NNS|NNP|NNPS>+}
	# """
	grammar = r"""
		NBAR: {<NN.*|JJ.*>+<NN.*>}
		NP: {<NBAR>}
			{<NBAR><IN><NBAR>}
	"""
	
	cp = RegexpParser(grammar)
	text = word_tokenize(data)
	sentence = pos_tag(text)
	result = []
	parsed_sentence = cp.parse(sentence)
	# # Clearer visuals for debugging
	# print(parsed_sentence)
	# parsed_sentence.draw()
	for np in clean_np(parsed_sentence):
		result.append(np)
	# print("\nreview text is: {}".format(data))
	# print("\nbefore lowercase and lemmatization: {}".format(result))
	
	# This counts number of times the NPs appears in the input data(review + summary) 
	c.update(lower_and_lemma(result))

def lower_and_lemma(phrases):
	lemmatizer = WordNetLemmatizer()
	result = []
	for phrase in phrases:
		phrase = str.lower(phrase)
		result.append(' '.join(lemmatizer.lemmatize(p) for p in phrase.split()))
	return result

def clean_np(parsed_sentence):
	for subtree in parsed_sentence.subtrees():
		if subtree.label() == 'NP':
			yield ' '.join(word for word,tag in subtree.leaves() if not (tag == 'DT' and str.lower(word) in ['the', 'a', 'an', 'these', 'that', 'this', 'those']))

if __name__ == "__main__":
	sandbox()

# Not useful for now...

# def npchunk_features(sentence, i, history):
# 	word, pos = sentence[i]
# 	return {"pos": pos}


# class ConsecutiveNPChunkTagger(nltk.TaggerI):

# 	def __init__(self, train_sents):
# 		train_set = []
# 		for tagged_sent in train_sents:
# 			untagged_sent = nltk.tag.untag(tagged_sent)
# 			history = []
# 			for i, (word, tag) in enumerate(tagged_sent):
# 				featureset = npchunk_features(untagged_sent, i, history)
# 				train_set.append( (featureset, tag) )
# 				history.append(tag)
# 		self.classifier = nltk.MaxentClassifier.train(train_set, algorithm='megam', trace=0)
	
# 	def tag(self, sentence):
# 		history = []
# 		for i, word in enumerate(sentence):
# 			featureset = npchunk_features(sentence, i , history)
# 			tag = self.classifier.classify(featureset)
# 			history.append(tag)
# 		return zip(sentence, history)

# class ConsecutiveNPChunker(nltk.ChunkParserI):
# 	def __init__(self, train_sents):
# 		tagged_sents = [[((w,t), c) for (w,t,c) in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
# 		self.tagger = ConsecutiveNPChunkTagger(tagged_sents)

# 	def parse(self, sentence):
# 		tagged_sents = self.tagger.tag(sentence)
# 		conlltags = [(w,t,c,) for ((w,t), c) in tagged_sents]
# 		return nltk.chunk.conlltags2tree(conlltags)
