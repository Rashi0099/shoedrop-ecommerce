from django.urls import path
from apps.reviews.views import user_views

urlpatterns = [
    path('add/<int:product_id>/', user_views.add_review, name='add_review'),
]