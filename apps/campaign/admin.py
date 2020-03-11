from django.contrib import admin
from .models import (
    Province,
    Campaign,
    CampaignTargetDevice,
    CampaignContent,
)

admin.site.register(Province)
admin.site.register(Campaign)
admin.site.register(CampaignTargetDevice)
admin.site.register(CampaignContent)
