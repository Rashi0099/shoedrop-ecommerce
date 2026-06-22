from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from apps.orders.models import Order


def is_admin(user):
    return user.is_superuser

@staff_member_required(login_url='admin_login')
def admin_order_list(request):

    orders = Order.objects.select_related(
        'user'
    ).order_by('-created_at')

    context = {

        'orders': orders

    }

    return render(

        request,

        'admin/orders/order_list.html',

        context

    )

@staff_member_required(login_url='admin_login')
def admin_order_details(request, order_id):

    order = get_object_or_404(

        Order.objects.select_related(

            'user',

            'address'

        ).prefetch_related(

            'items__product_variant__images',

            'items__product_variant__product'

        ),

        id=order_id

    )

    return render(

        request,

        'admin/orders/order_detail.html',

        {

            'order': order

        }

    )



@staff_member_required(login_url='admin_login')
def admin_update_order_status(request, order_id):

    if request.method != 'POST':

        return redirect('admin_order_details', order_id)

    order = get_object_or_404(

        Order,

        id=order_id

    )

    status = request.POST.get('status')

    allowed_status = [

        'pending',

        'processing',

        'shipped',

        'delivered',

        'cancelled',

        'returned'

    ]

    if status in allowed_status:

        order.order_status = status

        order.save()

        messages.success(

            request,

            'Order status updated.'

        )

    return redirect(

        'admin_order_details',

        order_id=order.id

    )