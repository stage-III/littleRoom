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
            from pathlib import Path

            from PIL import Image

            old_path = Path(self.image.path)
            img = Image.open(old_path)
            img = img.convert('RGB')
            if img.width > 800:
                ratio = 800 / img.width
                img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)

            new_path = old_path.with_suffix('.webp')
            img.save(new_path, format='WEBP', quality=85)

            if old_path != new_path:
                old_path.unlink(missing_ok=True)

            new_name = Path(self.image.name).with_suffix('.webp')
            self.image.name = str(new_name)
            type(self).objects.filter(pk=self.pk).update(image=str(new_name))


class Equipment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return self.name
