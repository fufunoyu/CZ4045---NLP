from collections import Counter
from nltk import RegexpParser, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer

import pandas as pd
import tqdm
import re
import html.parser
import math
from .chunktagger import ConsecutiveNPChunker
from .__settings import amazon_review_file_loc

# grammar = r"""
	#     NP: {<PDT|DT>+<JJ|JJR|JJS>+<NN|NNS|NNP|NNPS>+}
	#         # {<NN|NNS|NNP|NNPS>+}
	# """
grammar = r"""
		NBAR: {<NN.*|JJ.*>+<NN.*>}
		NP: {<NBAR>}
			{<NBAR><IN><NBAR>}
		"""
regex_parser = RegexpParser(grammar)

chunk_parser = ConsecutiveNPChunker()
# chunk_parser.train_and_save() # only run this if the chunktagger file changes
chunk_parser.load()

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

def extract_top_20_from_reviews(amazonReviewDF):
	c = Counter()
	parser = regex_parser if mode == "regexp" else chunk_parser
	for index, d in tqdm.tqdm(amazonReviewDF.iterrows()):
		input_data = d.reviewText + " " + d.summary
		extract_np(c, input_data, parser)
		if index%100 == 0:
			print("\rfinished %d iterations" %index, end="")
	
	print("\n {}".format(c.most_common(20)))

def top_3(amazonReviewDF, mode="regexp"):
	pop_products = ['B005SUHPO6','B0042FV2SI','B008OHNZI0']
	parser = regex_parser if mode == "regexp" else chunk_parser
	for product in pop_products:
		c = Counter()
		df = amazonReviewDF.loc[amazonReviewDF.asin==product]
		for index, d in tqdm.tqdm(df.iterrows()):
			input_data = d.reviewText + " " + d.summary
			extract_np(c, input_data, parser)				
		print("\n10 representative noun phrases for {} are: {}".format(product, c.most_common(10)))

def extract_np(c, data, parser):	
	text = word_tokenize(data)
	sentence = pos_tag(text)
	result = []
	parsed_sentence = parser.parse(sentence)
	# # Clearer visuals for debugging
	# print(parsed_sentence)
	# parsed_sentence.draw()
	for np in clean_np(parsed_sentence):
		result.append(np)
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

# def tfidf_top_3():
# 	amazonReviewDF = pd.read_json(amazon_review_file_loc, lines=True)
# 	np_to_products = dict()
# 	c = Counter()
# 	products = ['B005SUHPO6','B0042FV2SI','B008OHNZI0']
# 	for product in products:		
# 		df = amazonReviewDF.loc[amazonReviewDF.asin==product]
# 		for index, d in df.iterrows():
# 			extract_np(c, d.reviewText)
# 		for noun_phrase in set(c.elements()):
# 			try:
# 				np_to_products[noun_phrase] += 1
# 			except KeyError:
# 				np_to_products[noun_phrase] = 0

# 	for noun_phrase in c.elements():
# 		c[noun_phrase] = c[noun_phrase] * math.log(len(products)/1+np_to_products[noun_phrase])
# def tfidf_extract_np(data):
	# grammar = r"""
	# 	NBAR: {<NN.*|JJ.*>+<NN.*>}
	# 	NP: {<NBAR>}
	# 		{<NBAR><IN><NBAR>}
	# """
	
	# cp = RegexpParser(grammar)
	# text = word_tokenize(data)
	# sentence = pos_tag(text)
	# result = []
	# parsed_sentence = cp.parse(sentence)
	# for np in clean_np(parsed_sentence):
	# 	result.append(np)
	# c = Counter()
	# return c.update(lower_and_lemma(result))

def main():
	# data = clean_dataset()
	# extract_top_20_from_reviews(data)
	data = pd.read_json(amazon_review_file_loc, lines=True)
	# mode = "chunktagger"
	mode = "regexp"
	print("mode is {}".format(mode))
	top_3(data, mode)

