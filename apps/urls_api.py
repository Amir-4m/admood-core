from django.urls import path, include

urlpatterns = [
    path('accounts/', include("apps.accounts.api.urls")),
    path('campaign/', include("apps.campaign.api.urls")),
]
