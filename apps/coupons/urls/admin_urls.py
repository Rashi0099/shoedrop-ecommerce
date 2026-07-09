from django.urls import path
from apps.coupons.views.admin_views import coupon_list, add_coupon, edit_coupon, delete_coupon

urlpatterns = [
    path('', coupon_list, name='coupon_list'),
    path('add/', add_coupon, name='add_coupon'),
    path('edit/<int:coupon_id>/', edit_coupon, name='edit_coupon'),
    path('delete/<int:coupon_id>/', delete_coupon, name='delete_coupon'),
]
