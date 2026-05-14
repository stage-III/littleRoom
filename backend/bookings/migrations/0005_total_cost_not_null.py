import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bookings', '0004_backfill_total_cost'),
    ]
    operations = [
        migrations.AlterField(
            model_name='booking',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
