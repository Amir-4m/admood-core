from rest_framework.routers import DefaultRouter

from .views import ProvinceViewSet, CampaignViewSet, TargetDeviceViewSet, ContentViewSet

router = DefaultRouter()
router.register('provinces', ProvinceViewSet)
router.register('campaigns', CampaignViewSet, basename='Campaign')
router.register(prefix=r'(?P<campaign_id>\d+)/target_devices', viewset=TargetDeviceViewSet,
                basename='CampaignTargetDevice')
router.register(prefix=r'(?P<campaign_id>\d+)/contents', viewset=ContentViewSet, basename='CampaignContent')

urlpatterns = router.urls
