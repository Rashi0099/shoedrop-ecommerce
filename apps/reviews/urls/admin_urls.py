from django.urls import path
from apps.reviews.views import admin_views

urlpatterns = [
    path('', admin_views.review_list, name='review_list'),
    path('toggle/<int:review_id>/', admin_views.toggle_review_status, name='toggle_review_status'),
]