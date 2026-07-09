from django.db import models
from django.conf import settings
from apps.products.models import Product

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)
    review_title = models.CharField(max_length=255, blank=True, null=True)
    review_text = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name} - {self.rating} Stars'
