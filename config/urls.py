"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('allauth.urls')),

    path('',include('apps.accounts.urls.user_urls')),
    path('admin-panel/',include('apps.accounts.urls.admin_urls')),

    path('addresses/',include('apps.addresses.urls.user_urls')),
    path('customers_list/',include('apps.addresses.urls.admin_urls')),

    path('cart/',include('apps.cart.urls.user_urls')),
    path('cart-managment/',include('apps.cart.urls.admin_urls')),

    path('category/',include('apps.category.urls.user_urls')),
    path('category-managment/',include('apps.category.urls.admin_urls')),

    path('offers/',include('apps.offers.urls.user_urls')),
    path('offers-management/',include('apps.offers.urls.admin_urls')),

    path('coupons/',include('apps.coupons.urls.user_urls')),
    path('coupons-management/',include('apps.coupons.urls.admin_urls')),

    path('orders/',include('apps.orders.urls.user_urls')),
    path('orders-managment/',include('apps.orders.urls.admin_urls')),

    path('payments/',include('apps.payments.urls.user_urls')),
    path('payments-managment/',include('apps.payments.urls.admin_urls')),

    path('shop/',include('apps.products.urls.user_urls')),
    path('products-managment/',include('apps.products.urls.admin_urls')),

    path('reviews/',include('apps.reviews.urls.user_urls')),
    path('reviews-managment/',include('apps.reviews.urls.admin_urls')),

    path('wishlist/',include('apps.wishlist.urls.user_urls')),
    path('wishlist-managment/',include('apps.wishlist.urls.admin_urls')),

    










]
