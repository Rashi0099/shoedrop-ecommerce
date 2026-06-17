from django.db import models

from apps.accounts.models import User
from apps.addresses.models import Address
from apps.products.models import ProductVariant


class Order(models.Model):

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    PAYMENT_METHOD = (
        ('COD', 'Cash On Delivery'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Wallet', 'Wallet'),
        ('GPay', 'Google Pay'),
    )

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default='COD'
    )

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='pending'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    coupon_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f'Order #{self.id}'


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        self.total = self.quantity * self.unit_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.order.id} - {self.product_variant}'