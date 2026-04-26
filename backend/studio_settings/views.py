from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudioSettings


class PublicSettingsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        s = StudioSettings.get_solo()
        return Response({
            'min_notice_days': s.min_notice_days,
            'allow_pay_on_day': s.allow_pay_on_day,
            'min_booking_hours': s.min_booking_hours,
        })
