from django.contrib import admin
from .models import (
    Category,
    MediumCategoryDisplayText,
    Publisher,
)

admin.site.register(Category)
admin.site.register(MediumCategoryDisplayText)
admin.site.register(Publisher)
