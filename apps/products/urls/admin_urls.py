from django.urls import path
from apps.products.views.admin_views import (
    product_list,
    add_product,
    edit_product,
    toggle_product_status,
    variant_list,
    add_variant,
    edit_variant,
    delete_variant,
    delete_product,
)

urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/', add_product, name='add_product'),
    path('edit/<int:product_id>/', edit_product, name='edit_product'),
    path('toggle-status/<int:product_id>/', toggle_product_status, name='toggle_product_status'),
    path('<int:product_id>/variants/', variant_list, name='variant_list'),
    path('<int:product_id>/variants/add/', add_variant, name='add_variant'),
    path('variants/<int:variant_id>/edit/', edit_variant, name='edit_variant'),
    path('variants/<int:variant_id>/delete/', delete_variant, name='delete_variant'),
    path('<int:product_id>/delete/', delete_product, name='delete_product'),
]