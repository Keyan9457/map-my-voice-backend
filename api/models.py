# api/models.py
from django.db import models

class Review(models.Model):
    # --- Existing Fields ---
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    taluk = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    other_area = models.CharField(max_length=200, blank=True)

    theme = models.CharField(max_length=200)
    caution = models.CharField(max_length=200, blank=True)
    rating = models.CharField(max_length=10) # 'Good' or 'Bad'
    
    # --- NEW FIELDS TO ADD ---
    comment = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    # --- END OF NEW FIELDS ---

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.theme} review for {self.country} - {self.rating}"