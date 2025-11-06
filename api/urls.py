# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 1. Import the new view
from .views import ReviewViewSet, get_map_data, get_chart_data, get_incident_reports

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('map-data/', get_map_data, name='map-data'),
    path('chart-data/', get_chart_data, name='chart-data'),
    # 2. Add the new URL for incidents
    path('incidents/', get_incident_reports, name='incident-reports'),
]