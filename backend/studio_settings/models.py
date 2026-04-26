from django.db import models
from solo.models import SingletonModel


class StudioSettings(SingletonModel):
    allow_pay_on_day = models.BooleanField(default=False)
    min_booking_hours = models.PositiveSmallIntegerField(default=1)
    min_notice_days = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Studio Settings'

    def __str__(self):
        return 'Studio Settings'


class StudioHours(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    day_of_week = models.PositiveSmallIntegerField(choices=DAYS, unique=True)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_open = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week']
        verbose_name_plural = 'Studio hours'

    def __str__(self):
        return self.get_day_of_week_display()


class ClosureDate(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return str(self.date)
