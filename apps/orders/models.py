from django.db import models

from apps.accounts.models import User
from apps.addresses.models import Address
from apps.products.models import ProductVariant


class OrderAddress(models.Model):
    

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=6)
    country = models.CharField(max_length=100, default='India')
    address_type = models.CharField(max_length=20, default='HOME')

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def from_address(cls, address: Address) -> 'OrderAddress':
        """Create and persist a snapshot from a live Address instance."""
        return cls.objects.create(
            full_name=address.full_name,
            phone_number=address.phone_number,
            address=address.address or '',
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
            address_type=address.address_type,
        )

    def __str__(self):
        return f'{self.full_name}, {self.city}'


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

        ('return_requested', 'Return Requested'),

        ('return_rejected', 'Return Rejected'),

        ('returned', 'Returned'),

    )

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        related_name='orders'

    )

    address = models.ForeignKey(

        OrderAddress,

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

    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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

    ITEM_STATUS = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('return_requested', 'Return Requested'),
        ('return_rejected', 'Return Rejected'),
        ('returned', 'Returned'),
    )

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

    item_status = models.CharField(

        max_length=20,

        choices=ITEM_STATUS,

        default='active'

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    def save(self, *args, **kwargs):

        self.total = self.quantity * self.unit_price

        super().save(*args, **kwargs)

    def __str__(self):

        return f'{self.order.id} - {self.product_variant}'


class Return(models.Model):

    RETURN_TYPE = (

        ('Exchange', 'Exchange'),

        ('Refund', 'Refund'),

    )

    REFUND_MODE = (

        ('Wallet', 'Wallet'),

        ('Original Payment', 'Original Payment'),

        ('GPay', 'GPay'),

        ('UPI', 'UPI'),

    )

    STATUS = (

        ('Pending', 'Pending'),

        ('Reviewing', 'Reviewing'),

        ('Approved', 'Approved'),

        ('Rejected', 'Rejected'),

        ('Refunded', 'Refunded'),

    )

    order = models.ForeignKey(

        Order,

        on_delete=models.CASCADE,

        related_name='returns'

    )

    order_item = models.ForeignKey(

        OrderItem,

        on_delete=models.CASCADE,

        related_name='returns'

    )

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE

    )

    return_type = models.CharField(

        max_length=20,

        choices=RETURN_TYPE

    )

    reason = models.TextField()

    comments = models.TextField(

        blank=True,

        null=True

    )

    refund_mode = models.CharField(

        max_length=30,

        choices=REFUND_MODE,

        blank=True,

        null=True

    )

    status = models.CharField(

        max_length=20,

        choices=STATUS,

        default='Pending'

    )

    pickup_address = models.ForeignKey(

        OrderAddress,

        on_delete=models.SET_NULL,

        blank=True,

        null=True

    )

    pickup_date = models.DateTimeField(

        blank=True,

        null=True

    )

    refund_amount = models.DecimalField(

        max_digits=10,

        decimal_places=2,

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

        return f'Return #{self.id}'


class ReturnImage(models.Model):

    return_request = models.ForeignKey(

        Return,

        on_delete=models.CASCADE,

        related_name='images'

    )

    image = models.ImageField(

        upload_to='returns/'

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    def __str__(self):

        return f'Image {self.id}'