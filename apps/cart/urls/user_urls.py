from django.urls import path
from apps.cart.views.user_views import cart_view, add_to_cart, remove_from_cart, update_cart_quantity

urlpatterns = [

    path('', cart_view, name='cart'),

    path('add/<int:variant_id>/', add_to_cart, name='add_to_cart'),

    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

    path('update/<int:item_id>/', update_cart_quantity, name='update_cart_quantity'),

]