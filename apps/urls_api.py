from django.urls import path, include

urlpatterns = [
    path('accounts/', include("apps.accounts.api.urls")),
    path('campaign/', include("apps.campaign.api.urls")),
    path('medium/', include("apps.medium.api.urls")),
    path('device/', include("apps.device.api.urls")),
    path('payment/', include("apps.payment.api.urls")),
    path('', include("apps.core.api.urls")),
]
