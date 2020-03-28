from django.urls import path
from .views import CampaignListCreateAPIView

urlpatterns = [
    path('campaigns/', CampaignListCreateAPIView.as_view(), name="token"),
]
