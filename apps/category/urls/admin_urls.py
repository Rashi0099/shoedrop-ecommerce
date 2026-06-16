from django.urls import path
from apps.category.views.admin_views import *

urlpatterns = [
    path(
        'categories/', 
        category_list, 
        name='category_list'
    ),
    path(
        'categories/add/', 
        add_category, 
        name='add_category'
    ),
    path(
        'categories/edit/<int:category_id>/', 
        edit_category, 
        name='edit_category'
    ),
    path(
        'categories/delete/<int:category_id>/', 
        delete_category, 
        name='delete_category'
    ),
    path(
        'subcategories/add/', 
        add_subcategory, 
        name='add_subcategory'
    ),
    path(
        'subcategories/edit/<int:subcategory_id>/', 
        edit_subcategory, 
        name='edit_subcategory'
    ),
    path(
        'subcategories/delete/<int:subcategory_id>/', 
        delete_subcategory, 
        name='delete_subcategory'
    ),
]