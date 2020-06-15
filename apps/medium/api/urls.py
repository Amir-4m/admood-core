from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.medium.api.views import PublisherViewSet, MediumCategoryViewSet
from .views import MediumViewSet

router = DefaultRouter()
router.register('publishers', PublisherViewSet)
router.register('categories', MediumCategoryViewSet)

urlpatterns = [
                  path('choices/', MediumViewSet.as_view({'get': 'list'})),
              ] + router.urls
