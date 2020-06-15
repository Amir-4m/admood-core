from rest_framework.routers import DefaultRouter

from .views import ProvinceViewSet, CampaignViewSet, ContentViewSet

router = DefaultRouter()
router.register('provinces', ProvinceViewSet)
router.register('campaigns', CampaignViewSet)
router.register(r'(?P<campaign_id>\d+)/contents', ContentViewSet)

urlpatterns = router.urls
