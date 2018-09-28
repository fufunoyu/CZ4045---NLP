import json
import re

from datetime import datetime
from django.db import transaction
from .models import AmazonReview
from settings import amazon_review_file_loc, amazon_review_word_dict_loc


def init_amazon_review_db():
    """ initialize the amazon review sqlite3 database with given dataset """
    count = 0
    batchCount = 1000
    bulk_items = []
    with open(amazon_review_file_loc, 'r') as f:
        for line in f:
            json_line = json.loads(line)
            json_line['reviewTime'] = datetime.strptime(json_line['reviewTime'], r'%m %d, %Y')
            bulk_items.append(AmazonReview(**json_line))
            count += 1
            if count % batchCount == 0:
                try:
                    AmazonReview.objects.bulk_create(bulk_items)
                except Exception as e:
                    print(e)
                print(str(count) + " of 190919")
                bulk_items.clear()

        # save remaining items
        if len(bulk_items) > 0:
            try:
                AmazonReview.objects.bulk_create(bulk_items)
            except Exception as e:
                print(e)
        print("all amazon reviews were saved to database")


def transform_amazon_review_db():
    """ clean the amazon reviews record for NLP processing """

    count = 0
    window_size = 10000

    amazonReviewToClean = AmazonReview.objects.filter(reviewText_noStopWords=None)
    totalItemCount = amazonReviewToClean.count()

    batchToClean = AmazonReview.objects.filter(reviewText_noStopWords=None)[0:window_size]
    while batchToClean.count() > 0:
        with transaction.atomic():
            for ar in batchToClean:
                ar.transform_text()
        count += window_size
        batchToClean = AmazonReview.objects.filter(reviewText_noStopWords=None)[0:window_size]
        print(str(count) + " of " + str(totalItemCount))
    print("all amazon reviews text were cleaned")


def init_amazon_keyword_dictionary():
    """ build twitter keyword dictionary from text2 feed """

    amazonReview = AmazonReview.objects.exclude(reviewText_noStopWords=None)
    count = 0
    batchCount = 1000
    totalItemCount = amazonReview.count()

    keyword_list = set()
    for ar in amazonReview:
        keyword_list = keyword_list | set((ar.reviewText_noStopWords).split())
        count += 1
        if count % batchCount == 0:
            print(str(count) + " of " + str(totalItemCount))
    print(str(totalItemCount) + " of " + str(totalItemCount))

    keyword_list = list(keyword_list)
    keyword_list = sorted(keyword_list)
    keywords_to_write = "\n".join(keyword_list)

    keywords_to_write = re.sub(r'\b\d+\b\n', "", keywords_to_write, 0)

    with open(amazon_review_word_dict_loc, 'a') as keyword_file:
        keyword_file.write(keywords_to_write)
