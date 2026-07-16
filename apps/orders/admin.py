from django.contrib import admin

from apps.orders.models import OrderAddress


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone_number', 'city', 'state', 'postal_code', 'created_at')
    search_fields = ('full_name', 'phone_number', 'city', 'state')
    readonly_fields = ('created_at',)
