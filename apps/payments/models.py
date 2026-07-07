from django.db import models

from apps.accounts.models import User


class Wallet(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - ₹{self.balance}'


class WalletTransaction(models.Model):

    TRANSACTION_TYPE = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)

    description = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} - ₹{self.amount}'
