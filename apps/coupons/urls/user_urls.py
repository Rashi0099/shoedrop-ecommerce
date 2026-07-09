from django.urls import path
from apps.coupons.views import user_views

urlpatterns = [
    path('apply/', user_views.apply_coupon, name='apply_coupon'),
    path('remove/', user_views.remove_coupon, name='remove_coupon'),
]
