import math
import matplotlib.pyplot as plt
import numpy as np

from dbmgr.models import AmazonReview
from settings import amazon_review_word_dict_loc, english_word_dict_loc, \
    filtered_amazon_review_word_dict_loc, filtered_amazon_review_word_dict_noNN_loc


class KeywordItem():
    def __init__(self, keyword):
        self.keyword = keyword
        self.numReviewMentioned = 0
        self.totalScore = 0
        self.sentiment = 0
        self.adjustedSentiment = 0
        self.scoreList = []
        self.numPosMentioned = 1
        self.numNegMentioned = 1

    def __str__(self):
        return self.keyword

    def set_word_sentiment(self):
        if self.numReviewMentioned != 0:
            self.sentiment = self.totalScore / self.numReviewMentioned

        # rare words are penalized on their impact to final sentiment value
        # self.adjustedSentiment = ((2 / (1 + math.exp(-1 * self.numReviewMentioned))) - 1) * self.sentiment
        self.adjustedSentiment = self.sentiment * (self.numPosMentioned / self.numNegMentioned)

    def update_keyword_statistics(self, amazonReview):
        self.numReviewMentioned += 1
        self.totalScore += float(amazonReview.overall)
        self.scoreList.append(float(amazonReview.overall))

        if float(amazonReview.overall) >= 3:
            self.numPosMentioned += 1
        if float(amazonReview.overall) <= 2:
            self.numNegMentioned += 1


def sentiment_word_analysis():

    with open(filtered_amazon_review_word_dict_noNN_loc) as f:
        keywords = f.read().splitlines()

    keywords_dict = dict(zip([x for x in keywords],
                                [KeywordItem(x) for x in keywords]))


    count = 0
    for ar in AmazonReview.objects.exclude(reviewText_noStopWords=None):
        reviewTextKeywordsList = (ar.reviewText_noStopWords).split()
        for word in reviewTextKeywordsList:
            if word in keywords_dict:
                keywords_dict[word].update_keyword_statistics(ar)

        count += 1
        if count % 10000 == 0:
            print(str(count) + ' done')

    for _, keywordItem in keywords_dict.items():
        keywordItem.set_word_sentiment()

    # sort by adjusted sentiment
    sorted_keywordItem = sorted(keywords_dict.items(), key=lambda kv: kv[1].adjustedSentiment, reverse=True)
    positive_keyword_top20 = [x[1] for x in sorted_keywordItem[:20]]
    negative_keyword_top20 = [x[1] for x in sorted_keywordItem[-20:][::-1]]

    # plot positive keyword statistics
    plt.rcdefaults()
    fig, ax = plt.subplots()

    plt_width = 0.35

    plt_label = [x.keyword for x in positive_keyword_top20]
    plt_value_adjustedSentiment = [x.adjustedSentiment for x in positive_keyword_top20]
    plt_value_Sentiment = [x.sentiment for x in positive_keyword_top20]

    plt_y_pos = np.arange(len(plt_label))
    ax.barh(plt_y_pos+plt_width/2, plt_value_adjustedSentiment, plt_width, align='center', color='IndianRed', ecolor='black', label='adjusted sentiment')
    ax.barh(plt_y_pos-plt_width/2, plt_value_Sentiment, plt_width, align='center', color='SkyBlue', ecolor='black', label='sentiment')

    ax.set_yticks(plt_y_pos)
    ax.set_yticklabels(plt_label)
    ax.invert_yaxis()
    ax.set_xlabel('Sentiment')
    ax.set_title('Top 20 positive word ranked by calculated sentiment')
    ax.legend()

    plt.show()


    # plot negative keyword statistics
    plt.rcdefaults()
    fig, ax = plt.subplots()

    plt_width = 0.35

    plt_label = [x.keyword for x in negative_keyword_top20]
    plt_value_adjustedSentiment = [x.adjustedSentiment for x in negative_keyword_top20]
    plt_value_Sentiment = [x.sentiment for x in negative_keyword_top20]

    plt_y_pos = np.arange(len(plt_label))
    ax.barh(plt_y_pos+plt_width/2, plt_value_adjustedSentiment, plt_width, align='center', color='IndianRed', ecolor='black', label='adjusted sentiment')
    ax.barh(plt_y_pos-plt_width/2, plt_value_Sentiment, plt_width, align='center', color='SkyBlue', ecolor='black', label='sentiment')

    ax.set_yticks(plt_y_pos)
    ax.set_yticklabels(plt_label)
    ax.invert_yaxis()
    ax.set_xlabel('Sentiment')
    ax.set_title('Top 20 negative word ranked by calculated sentiment')
    ax.legend()

    plt.show()
