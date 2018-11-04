from collections import Counter
from nltk import RegexpParser, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer

import pandas as pd
import tqdm
import re
import html.parser
import math
import pickle
from .chunktagger import ConsecutiveNPChunker
from .__settings import amazon_review_file_loc

# grammar structure
grammar = r"""
		NBAR: {<NN.*|JJ.*>+<NN.*>}
		NP: {<NBAR>}
			{<NBAR><IN><NBAR>}
		"""
regex_parser = RegexpParser(grammar)

### initializing chunker
chunk_parser = ConsecutiveNPChunker()
# uncomment these two lines if chunktagger is used
# # chunk_parser.train_and_save()
# chunk_parser.load()

# cleans dataset by removing URLs and converting all to lowercase
def clean_dataset():
	amazonReviewDF = pd.read_json(amazon_review_file_loc, lines=True)
	col_label = amazonReviewDF.columns.get_loc("reviewText") 
	url_regex = r"https?\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?"

	# print("before")
	# print(amazonReviewDF.iloc[1,2])
	count = 0
	for index, d in tqdm.tqdm(amazonReviewDF.iterrows()):
		
		review = d.reviewText
		review_lower = review.lower()
		review_no_html_code = html.parser.unescape(review_lower)
		review_no_url = re.sub(url_regex, '<URL>', review_no_html_code)

		amazonReviewDF.iloc[count,col_label] = review_no_url
		count += 1
	# print('after')
	# print(amazonReviewDF.iloc[1,2])

	return amazonReviewDF

# saves clean dataset into pickle file for re-use
def save_clean_dataset():
	cleaned_data = clean_dataset()
	pickle.dump(cleaned_data, open('clean_data.pickle', 'wb'))

# Loops through entire collection of all reviews, concatenates summary and review text, extracts the noun phrases and stores it in a Counter object
def extract_top_20_from_reviews(amazonReviewDF, mode="regexp"):
	c = Counter()
	parser = regex_parser if mode == "regexp" else chunk_parser
	for index, d in tqdm.tqdm(amazonReviewDF.iterrows()):
		input_data = d.reviewText + " " + d.summary
		extract_np(c, input_data, parser)
	
	print("\n {}".format(c.most_common(20)))

#Loops through top 3 products and takes the 10 more representative noun phrases
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

# This function is called for every review. It tokenizes the review, tags it with nltk's default POS tagger and parses it according to the grammar defined at the start of this file
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

# lemmatizes the noun phrases so that the main meaning is captured even if different reviews express it differently
def lower_and_lemma(phrases):
	lemmatizer = WordNetLemmatizer()
	result = []
	for phrase in phrases:
		phrase = str.lower(phrase)
		result.append(' '.join(lemmatizer.lemmatize(p) for p in phrase.split()))
	return result

# used to remove the POS tag and return the noun phrase in a readable form
def clean_np(parsed_sentence):
	for subtree in parsed_sentence.subtrees():
		if subtree.label() == 'NP':
			# DT tag was for the initial grammar structure
			yield ' '.join(word for word,tag in subtree.leaves() if not (tag == 'DT' and str.lower(word) in ['the', 'a', 'an', 'these', 'that', 'this', 'those']))

def five_reviews(amazonReviewDF, mode="regexp"):
	# 5 indexes chosen randomly from a RNG
	# 	>>> random.choices(range(190919), k=5)
	# [120506, 31131, 110263, 34134, 68458]	
	five_random_review_indexes = [120506, 31131, 110263, 34134, 68458]
	parser = regex_parser if mode == "regexp" else chunk_parser
		
	df = amazonReviewDF.iloc[five_random_review_indexes]
	for index, d in tqdm.tqdm(df.iterrows()):
		c = Counter()
		input_data = d.reviewText + " " + d.summary
		extract_np(c, input_data, parser)
		print("Review number: {}".format(index))
		print("Review Text and summary: {}".format(input_data))				
		print("representative noun phrases are: {}".format(list(c.elements())))

def main():
	# For cleaned dataset uncomment the two lines below and comment the third line but the difference is minimal
	# save_clean_dataset()
	# data = pickle.load(open('clean_data.pickle', 'rb'))
	data = pd.read_json(amazon_review_file_loc, lines=True)
	# # mode = "chunktagger"
	mode = "regexp"
	print("mode is {}".format(mode))
	top_3(data, mode)
	extract_top_20_from_reviews(data, mode)
	five_reviews(data, mode)


# initial grammar structure
# grammar = r"""
# 	    NP: {<PDT|DT>*<JJ|JJR|JJS>+<NN|NNS|NNP|NNPS>+}
# 	        # {<NN|NNS|NNP|NNPS>+}
# 	"""