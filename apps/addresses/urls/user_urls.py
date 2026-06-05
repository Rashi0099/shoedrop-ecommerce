from django.urls import path
from apps.addresses.views.user_views import *


urlpatterns =[
    path('',address_list,name='address_list'),
    path('add_address/',add_address,name='add_address'),
    path(
    'edit/<int:id>/',
    edit_address,
    name='edit_address'
),

path(
    'delete/<int:id>/',
    delete_address,
    name='delete_address'
),

]