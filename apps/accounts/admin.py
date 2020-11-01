from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, UserProfile, Verification


@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('phone_number', 'email')}),
        (_('Permissions'), {'fields': ('is_verified', 'status', 'is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'phone_number', 'email', 'is_active', 'is_staff')
    search_fields = ('username', 'phone_number', 'email')
    list_filter = ('is_active', 'is_verified')


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verify_code', 'created_time', 'verified_time',)
    search_fields = ('user', 'verify_code')
    list_filter = ('verify_type', 'created_time', 'verified_time')


admin.site.register(UserProfile)
