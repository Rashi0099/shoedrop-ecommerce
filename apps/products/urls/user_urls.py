from django.urls import path
from apps.products.views.user_views import *

urlpatterns = [

    path(
        '',
        shop,
        name='shop'
    ),
    path(
        '<int:product_id>/',
        product_detail,
        name='product_detail'
    ),

]