from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer
from django.http import JsonResponse
from django.db.models import Count, Case, When, FloatField, Q
from django.db.models.functions import Cast

# This helper function will get our base queryset based on URL filters
def get_filtered_queryset(request):
    """
    Reads 'theme' and 'country' from the request's query parameters
    and returns a filtered queryset.
    """
    queryset = Review.objects.all()
    theme_filter = request.GET.get('theme')
    country_filter = request.GET.get('country')

    if theme_filter:
        queryset = queryset.filter(theme=theme_filter)
    if country_filter:
        queryset = queryset.filter(country=country_filter)
        
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

