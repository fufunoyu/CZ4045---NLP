from django.db import models


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

    class Meta:
        ordering = ['-reviewTime']

    def __str__(self):
        return self.reviewerID
