from django.urls import path

from apps.orders.views.admin_views import *
urlpatterns = [

    path(

        'order-list/',

        admin_order_list,

        name='admin_order_list'

    ),

    path('order-details/<int:order_id>/',admin_order_details,name='admin_order_details'

    ),
    path('update-status/<int:order_id>/', admin_update_order_status,name='admin_update_order_status'

    ),
    path('return-list/',admin_return_list,name='admin_return_list' ),

    path('return-details/<int:return_id>/',admin_return_detail,name='admin_return_detail'),

    path('update-return/<int:return_id>/',admin_update_return_status,name='admin_update_return_status'),


    

]