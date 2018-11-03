import pandas as pd
import nltk
#import wordninja
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
#nltk.download()
from itertools import chain
from collections import Counter
from collections import OrderedDict
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk import sent_tokenize
from nltk.probability import FreqDist
import contractions
#import tqdm
import time
import datetime
import sys
import re
import string
import concurrent.futures
import multiprocessing
from multiprocessing import Pool
import pandas as pd
import random

from .__settings import sample_review_file_loc, amazon_review_file_loc, \
    amazon_review_word_dict_loc, clean_amazon_review_file_loc

# import dask.dataframe as dd
# from dask.multiprocessing import get
console_encoding = sys.getdefaultencoding()
num_processes = multiprocessing.cpu_count()
num_partitions = 5
num_cores = multiprocessing.cpu_count()

# create a parallizing function
def parallelize_dataframe(df, func):
    a,b,c,d,e = np.array_split(df, num_partitions)
    pool = Pool(num_cores)
    df = pd.concat(pool.map(func, [a,b,c,d,e]))
    pool.close()
    pool.join()
    return df

# import datasets
df = pd.DataFrame(pd.read_json(sample_review_file_loc, lines=True))
df = pd.DataFrame(pd.read_json(amazon_review_file_loc, lines=True))

# data cleaning part 1

# remove urls
def parallelize_regex_clean_text(df):
    df['reviewText'] = df['reviewText'].apply(lambda x: re.sub(r'https?\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_=]*)?', '', x, flags=re.MULTILINE))
    df['reviewText'] = df['reviewText'].apply(lambda x: re.sub(r'([\.\?\!])([A-Z])', r'\g<1> \g<2>', x, 0))
    return df

def datacleaningpart1():
    
    global df

    df = parallelize_dataframe(df, parallelize_regex_clean_text)


########## Popular Products and Frequent Reviewers ##########

def popular():
    # top 10 products
    print ("Top 10 products with most reviews:")
    print(df.asin.value_counts().nlargest(10))
    print ('')

    # top 10 reviewers
    print ("Top 10 reviewers:")
    print(df.reviewerID.value_counts().nlargest(10))
    print ('')

########## Sentence Segmentation ##########

# data cleaning part 2
def datacleaningpart2():
    global df
    
    # dropNAs
    df = df.dropna()

    # drop entries with no reviews
    df = df[df.reviewText != '']
    return df
                                                           
# define a function to get sentence length
def parallelizegetsentlen(df):
    df['sentencelength'] = df.apply(lambda x: len(sent_tokenize(x['reviewText'])), axis = 1)
    return df

# plotting graph
def plotgraph(freqdict, graphname, xlabel, ylabel):
    x = list(freqdict.keys())
    y = list(freqdict.values())
    plt.figure()
    plt.bar(x, y, width=1.0)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    #plt.show()
    plt.savefig(graphname + '.png')
    plt.clf()

# bulk of the code
def sentenceseg():
    global df
    df = parallelize_dataframe(df, parallelizegetsentlen)
    
    sentencecounts = df['sentencelength'].value_counts().to_dict()
    print('Sentence length appended')
    print ('')

    # ordering the frequency dictionary
    sentencecounts = OrderedDict(sorted(sentencecounts.items(), key=lambda t: t[0]))

    plotgraph(sentencecounts, "Sentence Segmentation", "# of sentences in a review", "# of reviews of each length")

    # sampling 3 short reviews and 2 long ones
    df1_elements = df[df.sentencelength < 5].sample(n=3)
    df2_elements = df[df.sentencelength > 15].sample(n=2)
    df_elements = pd.concat([df1_elements, df2_elements])
    df_elements.to_csv('sample_sentence_lengths.csv')


########## Tokenization and Stemming ##########

ps = PorterStemmer()
stemmedenglishstopwords = [ps.stem(word) for word in stopwords.words('english')]


def parallelizestrippunctuations(df):
    df['reviewText'] = df['reviewText'].apply(lambda x: ''.join([i for i in x if i not in string.punctuation]))
    return df

# remove contractions e.g. doesn't to does not
def parallelizefixcontractions(df):
    df['reviewText'] = df['reviewText'].apply(lambda x: contractions.fix(x))
    return df

# data cleaning part 3
def datacleaningpart3():
    global df
    # convert to lower case
    df['reviewText'] = df['reviewText'].str.lower()
    df = parallelize_dataframe(df, parallelizefixcontractions)
    df = parallelize_dataframe(df, parallelizestrippunctuations)

    return df

# define a function to tokenize text
def parallelizetokenizetext(df):
    df['tokenizedwords'] = df.apply(lambda x: nltk.word_tokenize(x['reviewText']), axis = 1)
    return df

def parallelizegetlengthoftokens(df):
    df['lengthoftokenized'] = df.apply(lambda x: len(set(x['tokenizedwords'])), axis = 1)
    return df

def parallelizestemtokens(df):
    df["stemmedwords"] = df['tokenizedwords'].apply(lambda x: [ps.stem(y) for y in x])
    return df

def parallelizegetlengthofstemmedtokens(df):
    df['lengthofstemmedtokens'] = df.apply(lambda x: len(set(x['stemmedwords'])), axis = 1)
    return df

def tokenandstem():

    # tokenizing words and counting number of unique words in each review
    global df
    df = parallelize_dataframe(df, parallelizetokenizetext)

    df = parallelize_dataframe(df, parallelizegetlengthoftokens)
    tokencounts = df['lengthoftokenized'].value_counts().to_dict()

    # ordering the frequency dictionary
    tokencounts = OrderedDict(sorted(tokencounts.items(), key=lambda t: t[0]))

    # removing values with too low value counts for better plots
    tokencounts = {k: v for k, v in tokencounts.items() if v > 10}

    # plotting frequency graph
    plotgraph(tokencounts, "Tokenized words without stemming", "# of words in a review", "# of reviews of each length")
    print ('Tokenizing done')
    print ('')

    # stemming the words and counting number of unique stemmed words in each review
    df = parallelize_dataframe(df, parallelizestemtokens)
    df = parallelize_dataframe(df, parallelizegetlengthofstemmedtokens)

    stemmedtokencounts = df['lengthofstemmedtokens'].value_counts().to_dict()

    # ordering the frequency dictionary
    stemmedtokencounts = OrderedDict(sorted(stemmedtokencounts.items(), key=lambda t: t[0]))

    # removing values with too low value counts for better plots
    stemmedtokencounts = {k: v for k, v in stemmedtokencounts.items() if v > 10}

    # plotting frequency graph
    plotgraph(stemmedtokencounts, "Tokenized words with stemming", "# of words in a review", "# of reviews of each length")
    print ('Stemming done')
    print ('')

    # create list of tokens
    listoftokens = df['tokenizedwords'].tolist()
    # flatten list of lists into single list
    listoftokens = list(chain.from_iterable(listoftokens))
    # remove stopwords
    listoftokens = filter(lambda v: v not in stopwords.words('english'), listoftokens)
    #listoftokens = [x for x in listoftokens if x.lower() not in stopwords.words('english')]
    print("List of tokens without stopwords created")
    print ('')
                
    # creating list of stemmed words
    listofstemmedwords = df['stemmedwords'].tolist()
    # flatten list of lists into single list
    listofstemmedwords = list(chain.from_iterable(listofstemmedwords))
    # remove stopwords
    listofstemmedwords = filter(lambda v: v not in stemmedenglishstopwords, listofstemmedwords)
    #listofstemmedwords = [x for x in listoftokens if x.lower() not in stemmedenglishstopwords]
    print("List of stemmed words without stopwords created")
    print ('')

    # frequencies before stemming
    print (Counter(listoftokens).most_common(20))
    print ('')

    # frequencies after stemming
    print (Counter(listofstemmedwords).most_common(20))
    print ('')

    # listing the stopwords used
    print ('List of stopwords: ')
    print (stopwords.words('English'))
    print('')

########## POS Tagging ##########

def postagging():
    # pos tagging 
    sampledf = df.sample(n=5)
    sampledf['selectedSentence'] = sampledf.apply(lambda x: random.choice(sent_tokenize(x['reviewText'])), axis = 1)
    sampledf['selectedSentencePosTag'] = sampledf.apply(lambda x: nltk.pos_tag(nltk.word_tokenize(x['selectedSentence'])), axis = 1)
    for index, row in sampledf.iterrows():
        print (row['selectedSentence'] + ' => ' + str(row['selectedSentencePosTag']) + '\n')
    print ('')

def main():
    t0 = time.time()
    datacleaningpart1()
    popular()
    t1 = time.time()
    print ("Time for popular: ", str(datetime.timedelta(seconds=int(t1 - t0))))
    print ('')
    datacleaningpart2()
    sentenceseg()
    t2 = time.time()
    print ("Time for sentenceseg: ", str(datetime.timedelta(seconds=int(t2 - t1))))
    print ('')
    datacleaningpart3()
    tokenandstem()
    t3 = time.time()
    print ("Time for tokenandstem: ", str(datetime.timedelta(seconds=int(t3 - t2))))
    print ('')
    postagging()
    t4 = time.time()
    print ("Time for postagging: ", str(datetime.timedelta(seconds=int(t4 - t3))))
    print ('')
    print ("Total time: ", str(datetime.timedelta(seconds=int(t4 - t0))))
                                           
