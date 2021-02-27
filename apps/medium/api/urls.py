from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.medium.api.views import PublisherViewSet, CategoryViewSet, UpdatePublisherViewSet
from .views import MediumViewSet

router = DefaultRouter()
router.register('update-publishers', UpdatePublisherViewSet, basename='update-publisher')

urlpatterns = [
                  path('choices/', MediumViewSet.as_view({'get': 'list'})),
                  path('publishers/<int:medium>/', PublisherViewSet.as_view({'get': 'list'})),
                  path('categories/<int:medium>/', CategoryViewSet.as_view({'get': 'list'}))
              ] + router.urls
