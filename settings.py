import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=re)#l0w$+h!y+%#@+5zl2rqvwhf8*(gpdv&rwyq&ebm^#vz2!'

# https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=twitterapi&count=2

INSTALLED_APPS = [
    'dbmgr',
]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cz4045_nlp.db',
    }
}

amazon_review_file_loc = 'dataset/CellPhoneReview.json'
amazon_review_word_dict_loc = 'dataset/AmazonKeyword.txt'
