from django.urls import path
from apps.wishlist.views import user_views

urlpatterns = [
    path('', user_views.wishlist_view, name='wishlist'),
    path('add/<int:variant_id>/', user_views.add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:item_id>/', user_views.remove_from_wishlist, name='remove_from_wishlist'),
]