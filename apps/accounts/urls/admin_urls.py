from django.urls import path

from apps.accounts.views.admin_views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', admin_login, name='admin_login'),

    path('', admin_dashboard, name='admin_dashboard'),

    path('profile/', admin_profile, name='admin_profile'),

    path('edit-profile/', admin_edit_profile, name='admin_edit_profile'),

    path('change-password/', admin_change_password, name='admin_change_password'),

    path('admin_logout/', admin_logout, name='admin_logout'),
   

    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)