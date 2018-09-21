from django.db import models
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer


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
        """ clean input text from stopwords, punctuation and stem it

        Args:
            input_text (str): text to remove stopwords and punctuations

        return:
            str: cleaned text

        """
        input_text = input_text.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        word_list = tokenizer.tokenize(input_text)
        filtered_words = [word for word in word_list if word not in stopwords.words('english')]
        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(word) for word in filtered_words]
        return " ".join(stemmed_words)

    def transform_text(self):
        """
        clean reviewText and save it to reviewText_noStopWords
        """
        filtered_words = self._clean_text(self.reviewText)
        self.reviewText_noStopWords = filtered_words
        self.save()
