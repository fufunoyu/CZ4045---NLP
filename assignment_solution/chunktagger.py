import nltk
from nltk.corpus import conll2000
import pickle


def npchunk_features(sentence, i, history):
    word, pos = sentence[i]
    if i == 0:
        _, prevpos = "<START>", "<START>"
    else:
        _, prevpos = sentence[i-1]
    if i == len(sentence)-1:
        _, nextpos = "<END>", "<END>"
    else:
        _, nextpos = sentence[i+1]
    return {"pos": pos,
            "word": word,
            "prevpos": prevpos,
            "nextpos": nextpos,
            "prevpos+pos": "%s+%s" % (prevpos, pos),
            "pos+nextpos": "%s+%s" % (pos, nextpos),
            "tags-since-dt": tags_since_dt(sentence, i)}

def tags_since_dt(sentence, i):
    tags = set()
    for _, pos in sentence[:i]:
        if pos == 'DT':
            tags = set()
        else:
            tags.add(pos)
    return '+'.join(sorted(tags))


class ConsecutiveNPChunkTagger(nltk.TaggerI):

    def __init__(self, train_sents):
        train_set = []
        for tagged_sent in train_sents:
            untagged_sent = nltk.tag.untag(tagged_sent)
            history = []
            for i, (_, tag) in enumerate(tagged_sent):
                featureset = npchunk_features(untagged_sent, i, history)
                train_set.append( (featureset, tag) )
                history.append(tag)
        # original algorithm was megam but difficult to download and compile???
        self.classifier = nltk.MaxentClassifier.train(train_set, algorithm='IIS', trace=0)
    
    def tag(self, sentence):
        history = []
        for i, _ in enumerate(sentence):
            featureset = npchunk_features(sentence, i , history)
            tag = self.classifier.classify(featureset)
            history.append(tag)
        return zip(sentence, history)

class ConsecutiveNPChunker(nltk.ChunkParserI):
    def __init__(self):
        self.train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
    
    def train_and_save(self):
        self.tagged_sents = [[((w,t), c) for (w,t,c) in nltk.chunk.tree2conlltags(sent)] for sent in self.train_sents]
        self.tagger = ConsecutiveNPChunkTagger(self.tagged_sents)
        pickle.dump(self.tagger, open('npchunker.pickle', 'wb'))
        print("finished training") 

    def load(self):
        self.tagger = pickle.load(open('npchunker.pickle', 'rb'))
       

    # this func not called because we want to load the model from memory instead of retraining it everytime. this func is the reference for test_chunker
    def parse(self, sentence):
        tagged_sents = self.tagger.tag(sentence)
        conlltags = [(w,t,c,) for ((w,t), c) in tagged_sents]
        return nltk.chunk.conlltags2tree(conlltags)