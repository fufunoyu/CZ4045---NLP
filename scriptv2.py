import pandas as pd
import nltk
import wordninja
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
#nltk.download()
from collections import Counter
from collections import OrderedDict
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk import sent_tokenize
from nltk.probability import FreqDist
import sys
console_encoding = sys.getdefaultencoding()

df = pd.DataFrame(pd.read_json('SampleReview.json', lines=True))
df = pd.DataFrame(pd.read_json('CellPhoneReview.json', lines=True))

# data cleaning part 1
# dropNAs
df.dropna()

# remove contractions using pycontractions

########## Popular Products and Frequent Reviewers ##########

# top 10 products
print(df.asin.value_counts().nlargest(10))

# top 10 reviewers
print(df.reviewerID.value_counts().nlargest(10))

########## Sentence Segmentation ##########

# appending sentence length
df['sentencelength'] = df.apply(lambda x: len(sent_tokenize(x['reviewText'])), axis = 1)
sentencecounts = df['sentencelength'].value_counts().to_dict()

# ordering the frequency dictionary
sentencecounts = OrderedDict(sorted(sentencecounts.items(), key=lambda t: t[0]))

# plotting graph
def plotgraph(freqdict, graphname):
    x = list(freqdict.keys())
    y = list(freqdict.values())
    plt.plot(x, y)
    #plt.show()
    plt.savefig(graphname + ".png")

plotgraph(sentencecounts, "sentence_length")

# sampling 3 short reviews and 2 long ones
df1_elements = df[df.sentencelength < 5].sample(n=3)
df2_elements = df[df.sentencelength > 15].sample(n=2)
df_elements = pd.concat([df1_elements, df2_elements])
df_elements.to_csv('sample_sentence_lengths.csv')

########## Tokenization and Stemming ##########


# data cleaning part 2
# remove puncuations
df['reviewText'] = df['reviewText'].str.replace('[^\w\s]','')

# tokenizing words and counting number of unique words in each review
df['tokenizedwords'] = df.apply(lambda x: nltk.word_tokenize(x['reviewText']), axis = 1)

# data cleaning part 3
# split up known compound words e.g. helloworld -> hello world
# df['tokenizedwords'] = df.apply((lambda x: wordninja.split(word) for word in x['reviewText']), axis = 1)


df['lengthoftokenized'] = df.apply(lambda x: len(set(x['tokenizedwords'])), axis = 1)
tokencounts = df['lengthoftokenized'].value_counts().to_dict()

# ordering the frequency dictionary
tokencounts = OrderedDict(sorted(tokencounts.items(), key=lambda t: t[0]))

# removing values with too low value counts
tokencounts = {k: v for k, v in tokencounts.items() if v > 5}

# plotting frequency graph
plotgraph(tokencounts, "tokenized_words_before_stemming")

# stemming the words and counting number of unique stemmed words in each review
stemmer = SnowballStemmer("english")
ps = PorterStemmer()
df['stemmedwords'] = df['tokenizedwords'].apply(lambda x: [ps.stem(y) for y in x])
df['lengthofstemmedtokens'] = df.apply(lambda x: len(x['stemmedwords']), axis = 1)
stemmedtokencounts = df['lengthofstemmedtokens'].value_counts().to_dict()

# ordering the frequency dictionary
stemmedtokencounts = OrderedDict(sorted(stemmedtokencounts.items(), key=lambda t: t[0]))

# removing values with too low value counts
stemmedtokencounts = {k: v for k, v in stemmedtokencounts.items() if v > 5}

# plotting frequency graph
plotgraph(stemmedtokencounts, "stemmed_words")

# creating list of tokens with stopwords removal
listoftokens = []
for row in df['tokenizedwords']:
    for word in row:
        if word.lower() not in stopwords.words('english'):
            listoftokens.append(word)
print("List of tokens without stopwords created")
            
# creating list of stemmed words
listofstemmedwords = []
listofwords = []
stemmedenglishwords = [ps.stem(word) for word in stopwords.words('english')]
for row in df['stemmedwords']:
    for word in row:
        if word.lower() not in stemmedenglishwords:
            listofstemmedwords.append(word)
print("List of stemmed words without stopwords created")

# frequencies before stemming
fdist1 = FreqDist(listoftokens)
print ("Most Frequent Words Before Stemming")
for word, frequency in fdist1.most_common(20):
    print(u'{};{}'.format(word, frequency))

# frequencies after stemming
fdist2 = FreqDist(listofstemmedwords)
print ("Most Frequent Words Before Stemming")
for word, frequency in fdist2.most_common(20):
    print(u'{};{}'.format(word, frequency))

# listing the stopwords used
print (stopwords.words('English'))
print('')

########## POS Tagging ##########

# pos tagging 
for row in df['tokenizedwords'].sample(n=5):
    print(nltk.pos_tag(row))
    print ('')
