from django.urls import path


from apps.accounts.views.user_views import landing_page,signup,login_view,profile,logout_view


urlpatterns=[
    path('',landing_page,name='landing_page'),
    path('signup/',signup,name='signup'),
    path('login/',login_view ,name='login'),
    path('profile/',profile,name='profile'),
    path('logout/',logout_view,name='logout'),
    

]