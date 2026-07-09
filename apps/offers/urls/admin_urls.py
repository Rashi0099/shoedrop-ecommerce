from django.urls import path
from apps.offers.views.admin_views import offer_list, add_offer, edit_offer, delete_offer

urlpatterns = [
    path('', offer_list, name='offer_list'),
    path('add/', add_offer, name='add_offer'),
    path('edit/<int:offer_id>/', edit_offer, name='edit_offer'),
    path('delete/<int:offer_id>/', delete_offer, name='delete_offer'),
]