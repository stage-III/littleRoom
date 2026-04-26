import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from bookings.models import Booking


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            metadata = intent['metadata']
            booking_id = metadata['booking_id'] if 'booking_id' in metadata else None
            if booking_id:
                Booking.objects.filter(
                    pk=booking_id,
                    stripe_payment_intent_id=intent['id'],
                ).update(payment_status=Booking.PaymentStatus.PAID)

        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            metadata = intent['metadata']
            booking_id = metadata['booking_id'] if 'booking_id' in metadata else None
            if booking_id:
                Booking.objects.filter(
                    pk=booking_id,
                    stripe_payment_intent_id=intent['id'],
                ).update(payment_status=Booking.PaymentStatus.PENDING)

        return HttpResponse(status=200)
