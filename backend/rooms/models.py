from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    size_sqm = models.PositiveSmallIntegerField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return self.name
