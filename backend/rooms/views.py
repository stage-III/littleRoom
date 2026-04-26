from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Room
from .serializers import RoomSerializer


class RoomListView(generics.ListAPIView):
    queryset = Room.objects.filter(is_active=True).prefetch_related('equipment')
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
