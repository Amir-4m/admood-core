from django.contrib import admin
from .models import (
    Category,
    MediumCategoryDisplayText,
    Platform,
    OS,
    OSVersion,
    Province,
    Campaign,
    CampaignTargetDevice,
    CampaignContent,
    Publisher
)

admin.site.register(Category)
admin.site.register(MediumCategoryDisplayText)
admin.site.register(Platform)
admin.site.register(OS)
admin.site.register(OSVersion)
admin.site.register(Province)
admin.site.register(Campaign)
admin.site.register(CampaignTargetDevice)
admin.site.register(CampaignContent)
admin.site.register(Publisher)
