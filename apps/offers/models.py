from django.db import models
from django.utils import timezone
from apps.products.models import Product


class Offer(models.Model):

    offer_title = models.CharField(max_length=200)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name='offers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def get_status(self):
        if not self.is_active:
            return "Inactive"
        now = timezone.now()
        if self.end_date and now > self.end_date:
            return "Expired"
        if self.start_date and now < self.start_date:
            return "Scheduled"
        return "Active"

    def __str__(self):
        return self.offer_title
