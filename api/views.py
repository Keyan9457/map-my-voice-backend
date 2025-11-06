from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer
from django.http import JsonResponse
from django.db.models import Count, Case, When, FloatField, Q
from django.db.models.functions import Cast
from datetime import timedelta
from django.utils.timezone import now
# This helper function will get our base queryset based on URL filters
def get_filtered_queryset(request):
    queryset = Review.objects.all()

    theme_filter = request.GET.get('theme')
    country_filter = request.GET.get('country')
    timeframe = request.GET.get('timeframe')  # <-- NEW

    if theme_filter:
        queryset = queryset.filter(theme=theme_filter)

    if country_filter:
        queryset = queryset.filter(country=country_filter)

    # TIME FILTER
    if timeframe == "7d":
        queryset = queryset.filter(created_at__gte=now() - timedelta(days=7))
    elif timeframe == "30d":
        queryset = queryset.filter(created_at__gte=now() - timedelta(days=30))
    # "all" → no filter

    return queryset
# This viewset (for submitting reviews) does NOT change
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# --- THIS FUNCTION IS UPDATED ---
def get_map_data(request):
    # 1. Start with the filtered queryset
    base_queryset = get_filtered_queryset(request)

    # 2. Perform aggregation on the filtered data
    data = base_queryset.values('country').annotate(
        total_reviews=Count('id'),
        good_reviews=Count(Case(When(rating='Good', then=1)))
    ).annotate(
        score=Cast('good_reviews', FloatField()) / Cast('total_reviews', FloatField())
    )
    
    formatted_data = {
        item['country']: {
            'score': item['score'],
            'total_reviews': item['total_reviews']
        } for item in data
    }
    return JsonResponse(formatted_data)

# --- THIS FUNCTION IS UPDATED ---
def get_chart_data(request):
    # 1. Start with the filtered queryset
    base_queryset = get_filtered_queryset(request)

    # 2. Get unique themes from the filtered data
    themes = list(base_queryset.order_by('theme').values_list('theme', flat=True).distinct())
    
    labels = []
    good_data = []
    bad_data = []

    for theme in themes:
        if not theme:
            continue
            
        labels.append(theme)
        
        # 3. Count reviews for each theme *within* the filtered data
        # For example, if country=India is filtered, this will only count reviews from India
        good_count = base_queryset.filter(theme=theme, rating='Good').count()
        good_data.append(good_count)
        
        bad_count = base_queryset.filter(theme=theme, rating='Bad').count()
        bad_data.append(bad_count)
        
    chart_data = {
        'labels': labels,
        'datasets': [
            { 'label': 'Good', 'data': good_data },
            { 'label': 'Bad', 'data': bad_data }
        ]
    }
    return JsonResponse(chart_data)

# api/views.py (add this at the end)

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_incident_reports(request):
    """
    This view returns all reviews that are incidents
    (i.e., 'Bad' rating and have a latitude/longitude).
    """
    # Filter for reviews that are 'Bad' AND have latitude/longitude
    incidents = Review.objects.filter(
        rating='Bad', 
        latitude__isnull=False, 
        longitude__isnull=False
    )

    # Serialize the data into a simple format for the map
    data = [
        {
            'id': incident.id,
            'latitude': incident.latitude,
            'longitude': incident.longitude,
            'theme': incident.theme,
            'report_type': incident.report_type,
            'comment': incident.comment
        } 
        for incident in incidents
    ]

    return Response(data)