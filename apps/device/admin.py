from django.contrib import admin
from .models import (
    Platform,
    OS,
    OSVersion,
)

admin.site.register(Platform)
admin.site.register(OS)
admin.site.register(OSVersion)
