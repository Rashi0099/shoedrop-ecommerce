from django.db import models
from django.utils import timezone
from apps.category.models import Category


class Coupon(models.Model):

    DISCOUNT_TYPES = (
        ('percentage', 'Percentage (%)'),
        ('flat', 'Flat Amount (₹)'),
    )

    coupon_name = models.CharField(max_length=100)
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_cart_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(default=1)
    applicable_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupons')
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_till = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_till and now > self.valid_till:
            return False
        return True

    def get_status(self):
        if not self.is_active:
            return "Inactive"
        now = timezone.now()
        if self.valid_till and now > self.valid_till:
            return "Expired"
        if self.valid_from and now < self.valid_from:
            return "Scheduled"
        return "Active"

    def __str__(self):
        return self.coupon_code
