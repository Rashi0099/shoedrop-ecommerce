from django.urls import path
from apps.orders.views.user_views import checkout, place_order

urlpatterns=[
    path('',checkout,name='checkout'),
    path('place-order/', place_order, name='place_order'),
]
