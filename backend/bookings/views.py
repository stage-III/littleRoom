from collections import defaultdict
from datetime import date as date_type
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room
from studio_settings.models import ClosureDate, StudioHours, StudioSettings

from .models import Booking
from .serializers import BookingCreateSerializer, BookingListSerializer

TZ = ZoneInfo('Europe/London')


class AvailabilityView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        date_param = request.query_params.get('date')
        if not date_param:
            return Response({'error': 'date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            query_date = date_type.fromisoformat(date_param)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        closed_response = Response({
            'is_open': False,
            'date': date_param,
            'rooms': [],
        })

        if ClosureDate.objects.filter(date=query_date).exists():
            return closed_response

        try:
            studio_hours = StudioHours.objects.get(day_of_week=query_date.weekday())
        except StudioHours.DoesNotExist:
            return closed_response

        if not studio_hours.is_open:
            return closed_response

        settings = StudioSettings.get_solo()
        min_duration = timedelta(hours=settings.min_booking_hours)
        slot_step = timedelta(minutes=15)

        day_open = datetime(
            query_date.year, query_date.month, query_date.day,
            studio_hours.open_time.hour, studio_hours.open_time.minute,
            tzinfo=TZ,
        )
        day_close = datetime(
            query_date.year, query_date.month, query_date.day,
            studio_hours.close_time.hour, studio_hours.close_time.minute,
            tzinfo=TZ,
        )
        # Use a midnight-to-midnight range to avoid relying on DB-level timezone
        # conversion which requires MySQL timezone tables to be populated
        day_start = datetime(query_date.year, query_date.month, query_date.day, 0, 0, tzinfo=TZ)
        day_end = day_start + timedelta(days=1)

        # Fetch all active (non-refunded) bookings for the day in one query, grouped by room
        bookings_qs = Booking.objects.filter(
            room__is_active=True,
            start_datetime__gte=day_start,
            start_datetime__lt=day_end,
        ).exclude(
            payment_status=Booking.PaymentStatus.REFUNDED,
        ).values('room_id', 'start_datetime', 'end_datetime').order_by('start_datetime')

        bookings_by_room = defaultdict(list)
        for b in bookings_qs:
            bookings_by_room[b['room_id']].append((b['start_datetime'], b['end_datetime']))

        rooms = Room.objects.filter(is_active=True)
        room_data = []

        for room in rooms:
            room_bookings = bookings_by_room[room.pk]
            slots = []
            cursor = day_open

            while cursor + min_duration <= day_close:
                # Check if cursor falls inside an existing booking
                covering = next(
                    (b for b in room_bookings if b[0] <= cursor < b[1]),
                    None,
                )
                if covering:
                    # Jump to end of this booking, keeping cursor in local time
                    cursor = covering[1].astimezone(TZ)
                    continue

                # Find how long we can book from cursor before the next booking starts
                future = [b for b in room_bookings if b[0] > cursor]
                free_until = min(f[0] for f in future) if future else day_close
                free_until = min(free_until, day_close)

                max_hours = min(int((free_until - cursor).total_seconds() // 3600), 24)

                if max_hours >= settings.min_booking_hours:
                    slots.append({
                        'start_time': cursor.isoformat(),
                        'max_hours': max_hours,
                    })

                cursor += slot_step

            room_data.append({
                'room_id': room.pk,
                'name': room.name,
                'slug': room.slug,
                'hourly_rate': str(room.hourly_rate),
                'slots': slots,
            })

        return Response({
            'is_open': True,
            'date': date_param,
            'open_time': studio_hours.open_time.strftime('%H:%M'),
            'close_time': studio_hours.close_time.strftime('%H:%M'),
            'min_booking_hours': settings.min_booking_hours,
            'rooms': room_data,
        })


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]


class BookingMineView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('room')
