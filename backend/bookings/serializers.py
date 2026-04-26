from datetime import timedelta
from zoneinfo import ZoneInfo

import stripe
from django.conf import settings as django_settings
from django.db import transaction
from rest_framework import serializers

from rooms.models import Room
from studio_settings.models import ClosureDate, StudioHours, StudioSettings

from .models import Booking

TZ = ZoneInfo('Europe/London')


class BookingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'slug']


class BookingCreateSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.filter(is_active=True))

    class Meta:
        model = Booking
        fields = ['room', 'start_datetime', 'end_datetime', 'payment_method', 'guest_email', 'guest_name']

    def validate(self, data):
        start = data['start_datetime'].astimezone(TZ)
        end = data['end_datetime'].astimezone(TZ)
        settings = StudioSettings.get_solo()
        min_duration = timedelta(hours=settings.min_booking_hours)

        if end <= start:
            raise serializers.ValidationError('End time must be after start time.')

        if start.minute % 15 != 0 or start.second != 0 or start.microsecond != 0:
            raise serializers.ValidationError('Start time must be on a 15-minute boundary.')

        duration = end - start

        if duration < min_duration:
            raise serializers.ValidationError(
                f'Minimum booking duration is {settings.min_booking_hours} hour(s).'
            )

        excess = duration - min_duration
        if int(excess.total_seconds()) % 3600 != 0:
            raise serializers.ValidationError('Duration must be a whole number of hours beyond the minimum.')

        if duration > timedelta(hours=24):
            raise serializers.ValidationError('Maximum booking duration is 24 hours.')

        date = start.date()

        if ClosureDate.objects.filter(date=date).exists():
            raise serializers.ValidationError('The studio is closed on this date.')

        try:
            hours = StudioHours.objects.get(day_of_week=date.weekday())
        except StudioHours.DoesNotExist:
            raise serializers.ValidationError('No studio hours are configured for this day.')

        if not hours.is_open:
            raise serializers.ValidationError('The studio is closed on this day.')

        day_open = start.replace(
            hour=hours.open_time.hour, minute=hours.open_time.minute, second=0, microsecond=0
        )
        day_close = start.replace(
            hour=hours.close_time.hour, minute=hours.close_time.minute, second=0, microsecond=0
        )

        if start < day_open or end > day_close:
            raise serializers.ValidationError(
                f'Booking must be within studio hours ({hours.open_time:%H:%M}–{hours.close_time:%H:%M}).'
            )

        # Silently override pay-on-day if user is not eligible
        user = self.context['request'].user
        if data.get('payment_method') == Booking.PaymentMethod.ON_DAY:
            eligible = (
                user.is_authenticated
                and user.allow_pay_on_day
                and settings.allow_pay_on_day
            )
            if not eligible:
                data['payment_method'] = Booking.PaymentMethod.UPFRONT

        if not user.is_authenticated and not data.get('guest_email'):
            raise serializers.ValidationError({'guest_email': 'This field is required for guest bookings.'})

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        room = validated_data['room']
        start = validated_data['start_datetime']
        end = validated_data['end_datetime']

        with transaction.atomic():
            overlap = Booking.objects.select_for_update().filter(
                room=room,
                start_datetime__lt=end,
                end_datetime__gt=start,
            ).exclude(payment_status=Booking.PaymentStatus.REFUNDED)
            if overlap.exists():
                raise serializers.ValidationError('This time slot is no longer available.')

            if user.is_authenticated:
                validated_data['user'] = user
                validated_data.pop('guest_email', None)
                validated_data.pop('guest_name', None)

            booking = Booking.objects.create(**validated_data)

        if (
            booking.payment_method == Booking.PaymentMethod.UPFRONT
            and django_settings.STRIPE_SECRET_KEY
        ):
            stripe.api_key = django_settings.STRIPE_SECRET_KEY
            duration_hours = int((end - start).total_seconds() / 3600)
            amount_pence = int(room.hourly_rate * duration_hours * 100)
            intent = stripe.PaymentIntent.create(
                amount=amount_pence,
                currency='gbp',
                metadata={'booking_id': booking.pk},
            )
            booking.stripe_payment_intent_id = intent.id
            booking.save(update_fields=['stripe_payment_intent_id'])
            booking._client_secret = intent.client_secret

        return booking


class BookingListSerializer(serializers.ModelSerializer):
    room = BookingRoomSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'room', 'start_datetime', 'end_datetime', 'payment_method', 'payment_status', 'created_at']
