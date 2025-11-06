# api/serializers.py
from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # This '__all__' is what automatically includes your new fields
        fields = '__all__'