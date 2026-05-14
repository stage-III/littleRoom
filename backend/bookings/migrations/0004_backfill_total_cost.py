from django.db import migrations


def populate_total_cost(apps, schema_editor):
    Booking = apps.get_model('bookings', 'Booking')
    for booking in Booking.objects.filter(total_cost__isnull=True).select_related('room'):
        hours = int((booking.end_datetime - booking.start_datetime).total_seconds() // 3600)
        booking.total_cost = booking.room.hourly_rate * hours
        booking.save(update_fields=['total_cost'])


class Migration(migrations.Migration):
    dependencies = [
        ('bookings', '0003_add_total_cost'),
    ]
    operations = [
        migrations.RunPython(populate_total_cost, migrations.RunPython.noop),
    ]
