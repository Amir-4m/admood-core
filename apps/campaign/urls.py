from django.urls import path
from .views import export_campaign_report_csv

urlpatterns = [
    path('<int:pk>/export-excel/', export_campaign_report_csv, name='export-excel'),
]
