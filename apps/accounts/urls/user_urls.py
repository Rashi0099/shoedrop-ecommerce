from django.urls import path
from django.conf import settings
from django.conf.urls.static import static



from apps.accounts.views.user_views import *
urlpatterns=[
    path('',landing_page,name='landing_page'),
    path('signup/',signup,name='signup'),
    path('login/',login_view ,name='login'),
    path('profile/',profile,name='profile'),
    path('logout/',logout_view,name='logout'),

    path('verify-otp/',verify_otp,name='verify_otp'),
    path('resend-otp/',resend_otp,name='resend_otp'),
    path('forgot-password/',forgot_password,name='forgot_password'),
    path('forgot-password-verify-otp/',forgot_password_verify_otp,name='forgot_password_verify_otp'),
    path('reset-password/',reset_password,name='reset_password'),
    path( 'change-password/',change_password,name='change_password'),
    path(
    'edit-profile/',edit_profile,name='edit_profile'),
    path(
    'verify-email-otp/',
    verify_email_otp,
    name='verify_email_otp'
),
    path('resend-email-otp/', resend_email_otp, name='resend_email_otp'),
    path('resend-reset-otp/', resend_reset_otp, name='resend_reset_otp'),

    

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )