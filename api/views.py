from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.db.models import Count, Avg
from .models import Review, Incident
from .serializers import ReviewSerializer, IncidentSerializer


# -------------------------------
# Review Submit (Create Review)
# -------------------------------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by("-id")
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        review = serializer.save()

        # If review is BAD → create or update Incident
        if review.rating == "Bad" and review.latitude and review.longitude:
            
            # Check if an incident at this location & theme already exists
            existing_incident = Incident.objects.filter(
                theme=review.theme,
                report_type=review.report_type,
                latitude=review.latitude,
                longitude=review.longitude
            ).first()

            if existing_incident:
                # Update comment (optional: append)
                if review.comment:
                    existing_incident.comment = review.comment
                existing_incident.save()
            else:
                # Create new incident record
                Incident.objects.create(
                    theme=review.theme,
                    report_type=review.report_type,
                    comment=review.comment,
                    latitude=review.latitude,
                    longitude=review.longitude,
                    upvotes=0
                )


# -------------------------------
# Map Choropleth Data API
# -------------------------------
@api_view(["GET"])
def get_map_data(request):
    # Group reviews by country and calculate sentiment scores
    reviews = Review.objects.values("country").annotate(
        total_reviews=Count("id"),
        score=Avg(models.Case(
            models.When(rating="Good", then=1),
            models.When(rating="Bad", then=0),
            default=0,
        ))
    )

    data = {
        item["country"]: {
            "score": item["score"],
            "total_reviews": item["total_reviews"]
        }
        for item in reviews
    }

    return Response(data)


# -------------------------------
# Chart Analytics API
# -------------------------------
@api_view(["GET"])
def get_chart_data(request):
    grouped = Review.objects.values("theme").annotate(
        good=Count("id", filter=models.Q(rating="Good")),
        bad=Count("id", filter=models.Q(rating="Bad"))
    )

    return Response(grouped)


# -------------------------------
# Fetch Incident Pins for Map
# -------------------------------
@api_view(["GET"])
def get_incident_reports(request):
    incidents = Incident.objects.all().order_by("-upvotes")
    serializer = IncidentSerializer(incidents, many=True)
    return Response(serializer.data)


# -------------------------------
# ✅ Upvote API Endpoint
# -------------------------------
@api_view(["POST"])
def upvote_incident(request, incident_id):
    try:
        incident = Incident.objects.get(id=incident_id)
        incident.upvotes += 1
        incident.save()
        return Response({"upvotes": incident.upvotes}, status=200)

    except Incident.DoesNotExist:
        return Response({"error": "Incident not found"}, status=404)
