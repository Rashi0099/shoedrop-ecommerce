from django.urls import path

from apps.payments.views.user_views import (
    cod_payment,
    razorpay_payment,
    verify_razorpay_payment,
    wallet_payment,
    wallet
)

urlpatterns = [

    path('cod/', cod_payment,name='cod_payment'),
    path('razorpay/',razorpay_payment,name='razorpay_payment'),
    path('verify/',verify_razorpay_payment,name='verify_razorpay_payment'),
    path('wallet_payment/',wallet_payment,name='wallet_payment'),
    path('wallet/',wallet,name='wallet')

]