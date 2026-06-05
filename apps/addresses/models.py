from django.db import models
from django.conf import settings


class Address(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    full_name = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=10)

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=6)

    country = models.CharField(
        max_length=100,
        default='India'
    )

    address = models.TextField(null=True)

    address_type = models.CharField(
        max_length=20,
        choices=[
            ('HOME', 'Home'),
            ('WORK', 'Work'),
            ('OTHER', 'Other')
        ],
        default='HOME'
    )

    is_default = models.BooleanField(
        default=False
    )