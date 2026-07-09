from django.db import models
from django.conf import settings
from apps.products.models import ProductVariant


class CartItem(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.variant}"

    def get_total_price(self):
        return self.variant.get_offer_price() * self.quantity
