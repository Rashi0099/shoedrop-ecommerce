from django.urls import path

from apps.orders.views.user_views import (
    checkout,
    place_order,
    order_success,
    order_list,
    order_detail,
    download_invoice,
    return_order,
    cancel_order,
    cancel_item,
    return_item,
)


urlpatterns = [

    # Checkout flow
    path('checkout/', checkout, name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('order-success/', order_success, name='success_order'),




    path('order-list/',order_list,name='order_list'),
    path('order-details/<int:order_id>/', order_detail, name='order_details'),
    path('invoice/<int:order_id>/', download_invoice, name='download_invoice'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),

    path('return/<int:order_id>/',return_order, name='return_order'),


    path('cancel-item/<int:item_id>/', cancel_item,name='cancel_item'),
    path('return-item/<int:item_id>/', return_item,name='return_item'),
]