from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=11, unique=True)
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=10, blank=True)
    address = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
