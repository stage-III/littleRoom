from django.contrib import admin

from .models import Equipment, Room


class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'hourly_rate', 'size_sqm', 'is_active']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ['name']}
    inlines = [EquipmentInline]
