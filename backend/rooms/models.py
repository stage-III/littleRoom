from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    size_sqm = models.PositiveSmallIntegerField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            from PIL import Image

            img = Image.open(self.image.path)
            img = img.convert('RGB')
            if img.width > 800:
                ratio = 800 / img.width
                img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
            img.save(self.image.path, format='JPEG', quality=85, optimize=True)


class Equipment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return self.name
