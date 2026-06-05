from django.urls import path
from apps.addresses.views.admin_views import *
from django.db.models import Q


urlpatterns = [
   path(
    'customers/',
    customer_list,
    name='customer_list'
),

path(
    'customers/<int:id>/',
    customer_details,
    name='admin_customer_details'
),

path(
    'customers/block/<int:id>/',
    block_user,
    name='block_user'
),

path(
    'customers/unblock/<int:id>/',
    unblock_user,
    name='unblock_user'
),
]




@staff_member_required(login_url='admin_login')
def customer_list(request):

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    role = request.GET.get('role', '')

    users = User.objects.filter(
        is_superuser=False
    )

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    if status == 'active':
        users = users.filter(
            is_active=True
        )

    elif status == 'blocked':
        users = users.filter(
            is_active=False
        )

    if role == 'staff':
        users = users.filter(
            is_staff=True
        )

    elif role == 'customer':
        users = users.filter(
            is_staff=False
        )

    users = users.order_by(
        '-date_joined'
    )

    context = {
        'users': users,
        'search': search,
        'status': status,
        'role': role
    }

    return render(
        request,
        'admin/customers/customer_list.html',
        context
    )


        





                                 
        
