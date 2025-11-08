from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet,
    get_map_data,
    get_chart_data,
    get_incident_reports,
    upvote_incident
)

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),

    # Map and Chart Analytics
    path('map-data/', get_map_data, name='map-data'),
    path('chart-data/', get_chart_data, name='chart-data'),

    # Incident Reports (list)
    path('incidents/', get_incident_reports, name='incident-reports'),

    # Incident Upvote Endpoint
    path('incidents/<int:incident_id>/upvote/', upvote_incident, name='upvote-incident'),
]
