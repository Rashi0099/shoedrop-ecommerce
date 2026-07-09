from django.db import models
from apps.category.models import Category, SubCategory


class Product(models.Model):

    product_name = models.CharField(
        max_length=255
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )


    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE
    )

    description = models.TextField()

    product_features = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.product_name
    

class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    size = models.CharField(
        max_length=50
    )

    color = models.CharField(
        max_length=50
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def get_offer_price(self):
        max_discount = self.get_discount_percentage()
        if max_discount > 0:
            discount_amount = (self.price * max_discount) / 100
            return self.price - discount_amount
        return self.price

    def get_discount_percentage(self):
        max_discount = 0
        for offer in self.product.offers.filter(is_active=True):
            if offer.is_valid() and offer.discount_percentage > max_discount:
                max_discount = offer.discount_percentage
        return max_discount

class VariantImage(models.Model):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='products/'
    )

    is_primary = models.BooleanField(
        default=False
    )


