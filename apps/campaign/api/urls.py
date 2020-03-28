from rest_framework.routers import DefaultRouter

from .views import ProvinceViewSet, CampaignViewSet, TargetDeviceViewSet, ContentViewSet

router = DefaultRouter()
router.register('provinces', ProvinceViewSet)
router.register('campaigns', CampaignViewSet)
router.register(prefix=r'(?P<campaign_id>\d+)/target_devices', viewset=TargetDeviceViewSet, basename='CampaignContent')
router.register('contents', ContentViewSet)

urlpatterns = router.urls
