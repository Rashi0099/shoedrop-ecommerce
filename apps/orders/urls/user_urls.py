from django.urls import path
from apps.orders.views.user_views import *

urlpatterns = [
    path('checkout/',checkout, name='checkout'),
    path('place-order/',place_order, name='place_order'),
    path('wallet-payment/', wallet_payment, name='wallet_payment'),
    path('razorpay-payment/', razorpay_payment, name='razorpay_payment'),
    path('order-success/', order_success, name='success_order'),
    path('order_list/',order_list,name='order_list'),
    path(
    'order_details/<int:order_id>/',
    order_detail,
    name='order_details'
),
    path(
        'return-order/<int:order_id>/',
        return_order,
        name='return_order'
    )
]