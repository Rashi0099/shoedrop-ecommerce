from django.urls import path
from apps.addresses.views.admin_views import *

urlpatterns = [
    path(
        'customers/',
        customer_list,
        name='customer_list'
    ),
    path(
        'customers/<int:id>/',
        customer_details,
        name='admin_customer_details'
    ),
    path(
        'customers/block/<int:id>/',
        block_user,
        name='block_user'
    ),
    path(
        'customers/unblock/<int:id>/',
        unblock_user,
        name='unblock_user'
    ),
    path(
        'customers/delete/<int:id>/',
        delete_user,
        name='delete_user'
    ),
]
