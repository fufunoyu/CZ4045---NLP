from dbmgr.models import AmazonReview
from nltk import RegexpParser, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
# from nltk.corpus import conll2000
from collections import Counter

def sandbox():
	c = Counter()
	data = AmazonReview.objects.filter(asin='B005SUHPO6')[4:5]
	for index, d in enumerate(data):
		extract_np(c, d.reviewText)
		if index%100 == 0:
			print("\rfinished %d iterations" %index, end="") 
	
	print("\n {}".format(c.most_common(20)))

def extract_top_20_from_reviews():
	c = Counter()
	data = AmazonReview.objects.all()
	for index, d in enumerate(data):
		#we want to use as much information as possible so we put both the reviewText and summary together. 
		input_data = d.reviewText + " " + d.summary
		extract_np(c, input_data)
		if index%100 == 0:
			print("\rfinished %d iterations" %index, end="") 
	
	print("\n {}".format(c.most_common(20)))

def repr_np_from_3_popular_products():
	pop_products = ['B005SUHPO6','B0042FV2SI','B008OHNZI0']
	for product in pop_products:
		c = Counter()
		data = AmazonReview.objects.filter(asin=product)
		for index, d in enumerate(data):
			extract_np(c, d.reviewText)
			if index % 100 == 0:
				print("\rjust finished {} iterations".format(index), end="")
	
		print("\n10 representative noun phrases for {} are: {}".format(product, c.most_common(10)))

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