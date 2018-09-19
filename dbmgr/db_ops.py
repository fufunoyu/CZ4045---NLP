import json

from datetime import datetime
from .models import AmazonReview


amazon_review_file_loc = 'dataset/CellPhoneReview.json'
# amazon_review_file_loc = 'dataset/SampleReview.json'


def init_amazon_review_db():
    """ initialize the amazon review sqlite3 database with given dataset """
    count = 0
    bulk_items = []
    with open(amazon_review_file_loc, 'r') as f:
        for line in f:
            json_line = json.loads(line)
            json_line['reviewTime'] = datetime.strptime(json_line['reviewTime'], r'%m %d, %Y')
            bulk_items.append(AmazonReview(**json_line))
            count += 1
            if count % 1000 == 0:
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
