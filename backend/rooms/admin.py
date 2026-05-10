from django.contrib import admin
from django.utils.html import format_html

from .models import Equipment, Room


class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'hourly_rate', 'size_sqm', 'is_active']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['image_preview']
    inlines = [EquipmentInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;">', obj.image.url)
        return '—'
    image_preview.short_description = 'Preview'
