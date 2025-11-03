# api/models.py
from django.db import models

class Review(models.Model):
    # Fields for location
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    taluk = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    other_area = models.CharField(max_length=200, blank=True)

    # Fields for the review content
    theme = models.CharField(max_length=200)
    caution = models.CharField(max_length=200, blank=True)
    rating = models.CharField(max_length=10) # 'Good' or 'Bad'
    review_text = models.TextField(blank=True)

    # A timestamp that is automatically added when a review is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.theme} review for {self.country} - {self.rating}"