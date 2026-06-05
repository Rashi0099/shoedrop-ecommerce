from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):

    email = models.EmailField(unique=True)

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    is_blocked = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True,null=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,null=True
    )

    def save(self, *args, **kwargs):

        if not self.referral_code:
            self.referral_code = (
                str(uuid.uuid4())
                .replace('-', '')[:8]
                .upper()
            )

        super().save(*args, **kwargs)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email