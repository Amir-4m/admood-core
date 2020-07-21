from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.medium.api.views import PublisherViewSet, CategoryViewSet
from .views import MediumViewSet

router = DefaultRouter()
router.register('publishers', PublisherViewSet)
router.register('categories', CategoryViewSet)

urlpatterns = [
                  path('choices/', MediumViewSet.as_view({'get': 'list'})),
              ] + router.urls
