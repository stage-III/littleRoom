from allauth.account.admin import EmailAddressAdmin as AllauthEmailAddressAdmin
from allauth.account.models import EmailAddress as AllauthEmailAddress
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailAddress, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Studio Permissions', {'fields': ('allow_pay_on_day',)}),
    )
    list_display = ['email', 'first_name', 'last_name', 'allow_pay_on_day', 'is_active', 'is_staff']

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(AllauthEmailAddress)


@admin.register(EmailAddress)
class EmailAddressAdmin(AllauthEmailAddressAdmin):
    pass
