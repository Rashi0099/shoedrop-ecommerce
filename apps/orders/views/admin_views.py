from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from apps.orders.models import Order
from apps.orders.models import Return

def is_admin(user):
    return user.is_superuser

@staff_member_required(login_url='admin_login')
def admin_order_list(request):

    orders = Order.objects.select_related(
        'user'
    )

    query = request.GET.get('q')
    if query:
        from django.db.models import Q
        if query.startswith('SV-') and query[3:].isdigit():
            orders = orders.filter(id=int(query[3:]))
        elif query.isdigit():
            orders = orders.filter(id=int(query))
        else:
            orders = orders.filter(
                Q(user__username__icontains=query) |
                Q(user__email__icontains=query)
            )

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['created_at', '-created_at']:
        orders = orders.order_by(sort_by)
    else:
        orders = orders.order_by('-created_at')

    from django.core.paginator import Paginator
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'search': query or '',
        'status': status_filter or '',
        'sort': sort_by or '',
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

    # Calculate subtotal based ONLY on active items
    active_items = order.items.filter(item_status='active')
    subtotal = sum(item.total for item in active_items)
    tax = round(float(subtotal) * 0.18, 2)

    return render(
        request,
        'admin/orders/order_detail.html',
        {
            'order': order,
            'subtotal': subtotal,
            'tax': tax
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
        # If admin is cancelling the entire order
        if status == 'cancelled' and order.order_status != 'cancelled':
            from decimal import Decimal
            active_items = order.items.filter(item_status='active')
            refund_total = Decimal(str(order.total_amount))
            for item in active_items:
                item.item_status = 'cancelled'
                item.save()
                # Restore stock
                variant = item.product_variant
                variant.stock += item.quantity
                variant.save()

            # Reset order total
            order.total_amount = 0

            # Wallet refund for paid orders
            if order.payment_status == 'paid' and order.payment_method in ['Wallet', 'Razorpay'] and refund_total > 0:
                from apps.payments.models import Wallet, WalletTransaction
                wallet, _ = Wallet.objects.get_or_create(user=order.user)
                wallet.balance += refund_total
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=refund_total,
                    transaction_type='credit',
                    description=f'Refund for Order #{order.id} cancelled by admin'
                )

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


@staff_member_required(login_url='admin_login')
def admin_return_list(request):
    from django.db.models import Q

    returns = Return.objects.select_related(
        'user',
        'order',
        'order_item',
        'order_item__product_variant',
        'order_item__product_variant__product'
    )

    # Search by customer username, email or product name
    query = request.GET.get('q', '').strip()
    if query:
        returns = returns.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(order_item__product_variant__product__product_name__icontains=query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        returns = returns.filter(status=status_filter)

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'created_at':
        returns = returns.order_by('created_at')
    elif sort_by == 'status':
        returns = returns.order_by('status', '-created_at')
    else:
        returns = returns.order_by('-created_at')

    from django.core.paginator import Paginator
    paginator = Paginator(returns, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'admin/orders/return_order_list.html',
        {
            'returns': page_obj,
            'status_filter': status_filter,
            'search': query,
            'sort': sort_by,
        }
    )

@staff_member_required(login_url='admin_login')
def admin_return_detail(request, return_id):

    # Get the specific return request with all related data
    return_request = get_object_or_404(
        Return.objects.select_related(
            'user',
            'order',
            'order_item',
            'order_item__product_variant',
            'order_item__product_variant__product',
            'pickup_address'
        ).prefetch_related(
            'images'
        ),
        id=return_id
    )

    return render(
        request,
        'admin/orders/return_order_details.html',
        {
            'return_request': return_request
        }
    )

@staff_member_required(login_url='admin_login')
def admin_update_return_status(request, return_id):

    if request.method != 'POST':
        return redirect('admin_return_detail', return_id)

    return_request = get_object_or_404(Return, id=return_id)
    status = request.POST.get('status')

    allowed = ['Pending', 'Reviewing', 'Approved', 'Rejected', 'Refunded']
    if status not in allowed:
        return redirect('admin_return_detail', return_id)

    return_request.status = status
    return_request.save()

    item = return_request.order_item
    order = return_request.order

    if status == 'Reviewing':
        item.item_status = 'return_requested'
    elif status == 'Approved' or status == 'Refunded':
        item.item_status = 'returned'
    elif status == 'Rejected':
        item.item_status = 'return_rejected'
    item.save()

    # Wallet refund when admin marks as Refunded
    if status == 'Refunded':
        from apps.orders.utils import calculate_item_refund_amount
        refund_amount = calculate_item_refund_amount(order, return_request.order_item)
        
        # Critical: Deduct from order total to prevent over-refunding subsequent cancellations
        order.total_amount = float(order.total_amount) - float(refund_amount)
        if order.total_amount < 0:
            order.total_amount = 0
            
        if return_request.refund_mode == 'Wallet':
            from apps.payments.models import Wallet, WalletTransaction
            wallet, _ = Wallet.objects.get_or_create(user=return_request.user)
        wallet.balance += refund_amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=refund_amount,
            transaction_type='credit',
            description=f'Refund for Return #{return_request.id} - Order #{order.id}'
        )

    all_items = order.items.all()

    has_active   = all_items.filter(item_status='active').exists()
    has_pending  = all_items.filter(item_status='return_requested').exists()
    has_returned = all_items.filter(item_status='returned').exists()
    has_rejected = all_items.filter(item_status='return_rejected').exists()

    if has_active or has_pending:
        order.order_status = 'return_requested'

    elif has_returned and not has_rejected:
        order.order_status = 'returned'

    elif has_rejected and not has_returned:
        order.order_status = 'return_rejected'

    else:
        order.order_status = 'return_requested'

    order.save()

    messages.success(request, f'Return status updated to {status}.')
    return redirect('admin_return_detail', return_id)