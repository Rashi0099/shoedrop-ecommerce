from django.urls import path
from apps.orders.views.user_views import *

urlpatterns=[
    path('',checkout,name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('confirm_order/',order_success,name='success_order'),

]
