from dbmgr.models import AmazonReview
from nltk import RegexpParser, word_tokenize, pos_tag
from collections import Counter

def extract_top_20_from_reviews():
	c = Counter()
	data = AmazonReview.objects.all()[1000:2000]
	for index, d in enumerate(data):
		extract_np(c, d.reviewText)
		if index%100 == 0:
			print("\rfinished %d iterations" %index, end="") 
	
	print(c.most_common(20))

def repr_np_from_3_popular_products():
	pop_products = ['B005SUHPO6','B0042FV2SI','B008OHNZI0']
	for product in pop_products:
		c = Counter()
		data = AmazonReview.objects.filter(asin=product)
		for index, d in enumerate(data):
			extract_np(c, d.reviewText)
			if index % 100 == 0:
				print("\rjust finished {} iterations".format(index), end="")
	
		print("10 representative noun phrases for {} are: {}".format(product, c.most_common(10)))

def extract_np(c, data):
	#refine the grammar?
	grammar = r"""
        NP: {<PDT>?<DT>?<JJ|JJR|JJS>+<NN|NNS|NNP|NNPS>+}
            # {<NN|NNS|NNP|NNPS>+}
    """
    
	cp = RegexpParser(grammar)

	text = word_tokenize(data)
	sentence = pos_tag(text)
    
	parsed_sentence = cp.parse(sentence)
	# Clearer visuals for debugging
	# print(parsed_sentence)
	# parsed_sentence.draw()
	result = []
	for np in clean_np(parsed_sentence):
		result.append(np)
	
	c.update(result)

def clean_np(parsed_sentence):
    for subtree in parsed_sentence.subtrees():
        if subtree.label() == 'NP':
        	yield ' '.join(word for word, tag in subtree.leaves())



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