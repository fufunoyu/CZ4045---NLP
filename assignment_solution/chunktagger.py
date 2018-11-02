import nltk
import noun_phrase_summarizer as np
from nltk.corpus import conll2000
import pickle


def npchunk_features(sentence, i, history):
    word, pos = sentence[i]
    return {"pos": pos}


class ConsecutiveNPChunkTagger(nltk.TaggerI):

    def __init__(self, train_sents):
        train_set = []
        for tagged_sent in train_sents:
            untagged_sent = nltk.tag.untag(tagged_sent)
            history = []
            for i, (word, tag) in enumerate(tagged_sent):
                featureset = npchunk_features(untagged_sent, i, history)
                train_set.append( (featureset, tag) )
                history.append(tag)
        # original algorithm was megam but difficult to download and compile???
        self.classifier = nltk.MaxentClassifier.train(train_set, algorithm='IIS', trace=0)
    
    def tag(self, sentence):
        history = []
        for i, word in enumerate(sentence):
            featureset = npchunk_features(sentence, i , history)
            tag = self.classifier.classify(featureset)
            history.append(tag)
        return zip(sentence, history)

class ConsecutiveNPChunker(nltk.ChunkParserI):
    def __init__(self, train_sents):
        tagged_sents = [[((w,t), c) for (w,t,c) in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
        self.tagger = ConsecutiveNPChunkTagger(tagged_sents)
        pickle.dump(self.tagger, open('npchunker.pickle', 'wb'))

    def parse(self, sentence):
        tagged_sents = self.tagger.tag(sentence)
        conlltags = [(w,t,c,) for ((w,t), c) in tagged_sents]
        return nltk.chunk.conlltags2tree(conlltags)

def test_chunker(sentence):
    tagger = pickle.load(open('npchunker.pickle', 'rb'))
    tagged_sents = tagger.tag(sentence)
    conlltags = [(w,t,c,) for ((w,t), c) in tagged_sents]
    return nltk.chunk.conlltags2tree(conlltags)

if __name__ == "__main__":
    train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
    test_sents = conll2000.chunked_sents("test.txt", chunk_types = ['NP'])
    consecutive_chunker = ConsecutiveNPChunker(train_sents)
    print(consecutive_chunker.evaluate(test_sents))
    # test_data = np.clean_dataset()
