from django.urls import path

from .views import MediumViewSet

urlpatterns = [
    path('choices/', MediumViewSet.as_view({'get': 'list'})),
]
