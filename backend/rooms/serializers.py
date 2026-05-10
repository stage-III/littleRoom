from rest_framework import serializers

from .models import Equipment, Room


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'slug', 'description', 'size_sqm', 'hourly_rate', 'equipment', 'image']
