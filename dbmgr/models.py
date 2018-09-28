import re
from django.db import models
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


class AmazonReview(models.Model):
    """
    Model capturing amazon review
    """
    reviewerID = models.TextField()
    asin = models.TextField()
    reviewText = models.TextField()
    overall = models.DecimalField(max_digits=3, decimal_places=2) 
    summary = models.TextField()
    unixReviewTime = models.BigIntegerField()
    reviewTime = models.DateField()

    # additional fields defined to solve assignment
    reviewText_noStopWords = models.TextField(default=None, null=True)

    class Meta:
        ordering = ['-reviewTime']

    def __str__(self):
        return self.reviewerID

    def _clean_text(self, input_text):
        """ clean input text from stopwords, punctuation, etc

        Args:
            input_text (str): text to remove stopwords and punctuations

        return:
            str: cleaned text

        """
        input_text = input_text.lower()

        # remove url
        regex = r"https?\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?"
        input_text = re.sub(regex, "", input_text, 0)

        # add spaces between digit and alphabet
        input_text = re.sub(r'\b(\d+)([a-z]+)\b', r'\g<1> \g<2>', input_text, 0)

        # remove number
        input_text = re.sub(r'\b\d+\b', "", input_text, 0)

        # remove stopwords
        tokenizer = RegexpTokenizer(r'\w+')
        word_list = tokenizer.tokenize(input_text)
        filtered_words = [word for word in word_list if word not in stopwords.words('english')]

        return " ".join(filtered_words)

    def transform_text(self):
        """
        clean reviewText and save it to reviewText_noStopWords
        """
        filtered_words = self._clean_text(self.reviewText)
        self.reviewText_noStopWords = filtered_words
        self.save()
