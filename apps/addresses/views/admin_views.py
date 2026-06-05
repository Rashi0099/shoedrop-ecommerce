from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.models import User


@staff_member_required(login_url='admin_login')
def customer_list(request):

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    role = request.GET.get('role', '')

    users = User.objects.filter(is_superuser=False)

    if search:
        users = users.filter(username__icontains=search)
         

    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'blocked':
        users = users.filter(is_active=False)

    if role == 'staff':
        users = users.filter(is_staff=True)
    elif role == 'customer':
        users = users.filter(is_staff=False)

    users = users.order_by('-date_joined')

    context = {
        'users': users,
        'search': search,
        'status': status,
        'role': role
    }

    return render(request, 'admin/customers/customer_list.html', context)


@staff_member_required(login_url='admin_login')
def customer_details(request, id):

    customer = get_object_or_404(User, id=id, is_superuser=False)

    context = {
        'customer': customer
    }

    return render(request, 'admin/customers/customer_details.html', context)


@staff_member_required(login_url='admin_login')
def block_user(request, id):

    user = get_object_or_404(User, id=id, is_superuser=False)
    user.is_active = False
    user.save()

    return redirect('customer_list')


@staff_member_required(login_url='admin_login')
def unblock_user(request, id):

    user = get_object_or_404(User, id=id, is_superuser=False)
    user.is_active = True
    user.save()

    return redirect('customer_list')