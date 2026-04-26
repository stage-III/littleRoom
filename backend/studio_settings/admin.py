from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import ClosureDate, StudioHours, StudioSettings


@admin.register(StudioSettings)
class StudioSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(StudioHours)
class StudioHoursAdmin(admin.ModelAdmin):
    list_display = ['get_day_of_week_display', 'open_time', 'close_time', 'is_open']


@admin.register(ClosureDate)
class ClosureDateAdmin(admin.ModelAdmin):
    list_display = ['date', 'reason']
