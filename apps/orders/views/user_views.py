from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal


from apps.addresses.models import Address
from apps.cart.models import CartItem
from apps.products.models import ProductVariant
from apps.orders.models import Order, OrderItem, OrderAddress
from apps.coupons.models import Coupon
from apps.orders.models import Return, ReturnImage
from django.contrib import messages



@login_required(login_url='login')
def checkout(request):

    user_addresses = Address.objects.filter(user=request.user)

    checkout_items = []

    subtotal = 0

    buy_now_id = request.GET.get('buy_now')

    if buy_now_id:

        variant = get_object_or_404(ProductVariant, id=buy_now_id)

        if not variant.is_active or not variant.product.is_active or not variant.product.category.is_active:
            messages.error(request, 'Sorry, this product is currently unavailable.')
            return redirect('shop')

        if variant.stock < 1:
            messages.error(request, 'Sorry, this item is currently out of stock.')
            return redirect('shop')

        checkout_items.append({
            'variant': variant,
            'quantity': 1,
            'get_total_price': variant.get_offer_price()
        })

        subtotal = float(variant.get_offer_price())

    else:

        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('shop')

        for item in cart_items:

            if item.variant.is_deleted or not item.variant.is_active or item.variant.product.is_deleted or not item.variant.product.is_active or not item.variant.product.category.is_active:
                messages.error(request, f'"{item.variant.product.product_name}" is currently unavailable. Please remove it from your cart.')
                return redirect('cart')

            if item.variant.stock < item.quantity:
                messages.error(request, f'"{item.variant.product.product_name}" has insufficient stock. Please adjust your cart.')
                return redirect('cart')

            checkout_items.append({
                'variant': item.variant,
                'quantity': item.quantity,
                'get_total_price': item.get_total_price()
            })

            subtotal += item.get_total_price()

    gst = float(subtotal) * 0.18

    delivery_fee = 0
    
    coupon_discount = 0
    applied_coupon = None
    if 'applied_coupon' in request.session:
        try:
            coupon = Coupon.objects.get(coupon_code=request.session['applied_coupon'], is_active=True)
            if coupon.is_valid() and float(subtotal) >= float(coupon.min_cart_value):
                applied_coupon = coupon
                if coupon.discount_type == 'percentage':
                    coupon_discount = (float(subtotal) * float(coupon.discount_value)) / 100
                else:
                    coupon_discount = float(coupon.discount_value)
            else:
                del request.session['applied_coupon']
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']

    grand_total = float(subtotal) + gst + delivery_fee - coupon_discount
    if grand_total < 0:
        grand_total = 0
    
    coupons = Coupon.objects.filter(is_active=True)
    available_coupons = [c for c in coupons if c.is_valid()]

    context = {
        'addresses': user_addresses,
        'cart_items': checkout_items,
        'subtotal': subtotal,
        'gst': round(gst, 2),
        'delivery_charges': delivery_fee,
        'coupon_discount': round(coupon_discount, 2),
        'applied_coupon': applied_coupon,
        'grand_total': round(grand_total, 2),
        'available_coupons': available_coupons,
    }

    return render(request, 'user/orders/checkout.html', context)

@login_required(login_url='login')
def place_order(request):

    if request.method != 'POST':
        return redirect('checkout')

    from apps.payments.views.user_views import (
        cod_payment,
        razorpay_payment,
        wallet_payment,
    )

    payment_method = request.POST.get('payment_method')

    if not payment_method:
        messages.error(request, 'Please select a payment method.')
        return render(request, 'user/orders/checkout.html')

    if payment_method == 'cod':
        return cod_payment(request)

    elif payment_method == 'wallet':
        return wallet_payment(request)

    elif payment_method == 'razorpay':
        return razorpay_payment(request)

    return redirect('checkout')




def calculate_order_amount(request, buy_now_id=None):

    subtotal = 0
    items = []

    if buy_now_id:

        variant = get_object_or_404(ProductVariant, id=buy_now_id)

        if not variant.is_active or not variant.product.is_active or not variant.product.category.is_active:
            return None

        if variant.stock < 1:
            return None

        items.append({
            'variant': variant,
            'quantity': 1,
            'price': float(variant.get_offer_price())
        })

        subtotal = float(variant.get_offer_price())

    else:

        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return None

        for item in cart_items:

            if not item.variant.is_active or not item.variant.product.is_active or not item.variant.product.category.is_active:
                return None

            if item.variant.stock < item.quantity:
                return None

            items.append({
                'variant': item.variant,
                'quantity': item.quantity,
                'price': float(item.variant.get_offer_price())
            })

            subtotal += float(item.get_total_price())

    gst = subtotal * 0.18
    
    coupon_discount = 0
    applied_coupon_obj = None
    if 'applied_coupon' in request.session:
        try:
            from apps.coupons.models import Coupon
            from apps.orders.models import Order
            coupon = Coupon.objects.get(coupon_code=request.session['applied_coupon'], is_active=True)
            
            if coupon.is_valid() and subtotal >= float(coupon.min_cart_value):
                # Check if user already used this coupon (exclude cancelled orders)
                user_used_coupon = Order.objects.filter(
                    user=request.user,
                    coupon=coupon
                ).exclude(order_status='cancelled').exists()

                if user_used_coupon:
                    del request.session['applied_coupon']
                else:
                    if coupon.discount_type == 'percentage':
                        coupon_discount = (subtotal * float(coupon.discount_value)) / 100
                    else:
                        coupon_discount = float(coupon.discount_value)
                    applied_coupon_obj = coupon
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']

    grand_total = subtotal + gst - coupon_discount
    if grand_total < 0:
        grand_total = 0

    return {
        'subtotal': round(subtotal, 2),
        'gst': round(gst, 2),
        'coupon_discount': round(coupon_discount, 2),
        'grand_total': round(grand_total, 2),
        'amount_paise': int(grand_total * 100),
        'items': items,
        'coupon': applied_coupon_obj
    }


def create_order(request, payment_method, payment_status):

    address_id = request.POST.get('address_id')
    buy_now_id = request.POST.get('buy_now')

    if not address_id:
        return None

    live_address = get_object_or_404(Address, id=address_id, user=request.user)
    address = OrderAddress.from_address(live_address)

    totals = calculate_order_amount(request, buy_now_id)

    if not totals:
        return None

    order = Order.objects.create(
        user=request.user,
        address=address,
        payment_method=payment_method,
        payment_status=payment_status,
        order_status='pending',
        total_amount=totals['grand_total'],
        coupon_discount=totals.get('coupon_discount', 0),
        coupon=totals.get('coupon')
    )

    for item in totals['items']:

        OrderItem.objects.create(
            order=order,
            product_variant=item['variant'],
            quantity=item['quantity'],
            unit_price=item['price']
        )

        variant = item['variant']
        variant.stock -= item['quantity']
        variant.save()

    if not buy_now_id:
        CartItem.objects.filter(user=request.user).delete()

    # Clear the applied coupon from session after order is placed
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']

    return order






@login_required(login_url='login')
def order_success(request):

    order_id = request.GET.get('order_id')

    order = None

    if order_id:

        try:

            order = Order.objects.get(id=order_id, user=request.user)

        except Order.DoesNotExist:

            pass

    return render(request, 'user/orders/order_success.html', {'order': order})

@login_required(login_url='login')
def order_list(request):
    search = request.GET.get('q', '').strip()

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items__product_variant__product').order_by('-created_at')

    if search:
        from django.db.models import Q
        # Support "SD-123" or plain "123" as order ID search
        if search.upper().startswith('SD-') and search[3:].isdigit():
            orders = orders.filter(id=int(search[3:]))
        elif search.isdigit():
            orders = orders.filter(id=int(search))
        else:
            orders = orders.filter(
                items__product_variant__product__product_name__icontains=search
            ).distinct()

    from django.core.paginator import Paginator
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'search': search,
    }

    return render(
        request,
        'user/orders/order_list.html',
        context
    )

from apps.orders.utils import render_to_pdf

@login_required(login_url='login')
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Only include non-cancelled / non-returned items in the invoice totals.
    # Cancelled items have already been deducted from order.total_amount, but
    # we recalculate here so subtotal and GST are shown correctly per line.
    billable_items = order.items.exclude(item_status__in=['cancelled', 'returned', 'return_rejected'])
    subtotal = sum(item.total for item in billable_items)
    gst = subtotal * Decimal('0.18')

    context = {
        'order': order,
        'items': order.items.select_related(
            'product_variant__product'
        ).all(),
        'subtotal': round(subtotal, 2),
        'gst': round(gst, 2),
    }

    pdf_bytes = render_to_pdf('user/orders/invoice_pdf.html', context)

    if pdf_bytes:
        filename = f'ShoeDrop_Invoice_{order.id}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    messages.error(request, 'Could not generate invoice. Please try again.')
    return redirect('order_details', order_id=order.id)

@login_required(login_url='login')
def order_detail(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user

    )

    order_items = OrderItem.objects.filter(

        order=order

    ).select_related(

        'product_variant',

        'product_variant__product'

    )

    addresses = Address.objects.filter(user=request.user)

    context = {

        'order': order,

        'order_items': order_items,

        'addresses': addresses

    }

    return render(

        request,

        'user/orders/order_details.html',

        context

    )

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.order_status not in ['pending', 'processing']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('order_details', order_id=order.id)
        
    if request.method == 'POST':
        selected_item_ids = request.POST.getlist('selected_items')
        
        if not selected_item_ids:
            messages.error(request, 'Please select at least one item to cancel.')
            return redirect('order_details', order_id=order.id)
            
        items_to_cancel = order.items.filter(id__in=selected_item_ids, item_status='active')
        
        if not items_to_cancel.exists():
            messages.error(request, 'Selected items cannot be cancelled.')
            return redirect('order_details', order_id=order.id)
            
        # Check if we are cancelling all remaining active items
        active_items_count = order.items.filter(item_status='active').count()
        cancelling_all_remaining = (active_items_count == items_to_cancel.count())

        if cancelling_all_remaining:
            refund_total = float(order.total_amount)
            
            for item in items_to_cancel:
                item.item_status = 'cancelled'
                item.save()
                variant = item.product_variant
                variant.stock += item.quantity
                variant.save()

            order.total_amount = 0
            order.order_status = 'cancelled'
        else:
            refund_total = 0
            for item in items_to_cancel:
                item.item_status = 'cancelled'
                item.save()

                # Restore stock
                variant = item.product_variant
                variant.stock += item.quantity
                variant.save()

                # Deduct from order total using proper prorated amount
                from apps.orders.utils import calculate_item_refund_amount
                deduction_decimal = calculate_item_refund_amount(order, item)
                deduction_float = float(deduction_decimal)
                
                order.total_amount = float(order.total_amount) - deduction_float
                refund_total += deduction_float

            if order.total_amount < 0:
                order.total_amount = 0

        order.save()

        # Wallet refund for paid orders (Wallet or Razorpay)
        if order.payment_status == 'paid' and order.payment_method in ['Wallet', 'Razorpay'] and refund_total > 0:
            from apps.payments.models import Wallet, WalletTransaction
            from decimal import Decimal
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += Decimal(str(round(refund_total, 2)))
            wallet.save()
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=Decimal(str(round(refund_total, 2))),
                transaction_type='credit',
                description=f'Refund for cancelled items in Order #{order.id}'
            )

        messages.success(request, 'Selected items have been cancelled successfully.')

    return redirect('order_details', order_id=order.id)
@login_required(login_url='login')
def return_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.order_status not in ['delivered', 'return_requested']:
        return redirect('order_details', order.id)

    if request.method == 'POST':
        return_type = request.POST.get('return_type')
        reason = request.POST.get('reason')
        comments = request.POST.get('comments')
        refund_mode = request.POST.get('refund_mode')
        address_id = request.POST.get('pickup_address')
        images = request.FILES.getlist('images')
        selected_item_ids = request.POST.getlist('item_ids')

        if not selected_item_ids:
            messages.error(request, 'No items selected for return.')
            return redirect('order_details', order.id)

        live_pickup = get_object_or_404(Address, id=address_id, user=request.user)
        pickup_address = OrderAddress.from_address(live_pickup)

        items_to_return = order.items.filter(id__in=selected_item_ids, item_status='active')

        from apps.orders.utils import calculate_item_refund_amount
        for item in items_to_return:
            return_request = Return.objects.create(
                order=order,
                order_item=item,
                user=request.user,
                return_type=return_type,
                reason=reason,
                comments=comments,
                refund_mode=refund_mode,
                pickup_address=pickup_address,
                refund_amount=calculate_item_refund_amount(order, item)
            )

            for image in images:
                ReturnImage.objects.create(
                    return_request=return_request,
                    image=image
                )
            
            item.item_status = 'return_requested'
            item.save()

        order.order_status = 'return_requested'
        order.save()
        messages.success(request, 'Return request submitted.')
        return redirect('order_details', order.id)

    selected_items_str = request.GET.get('items', '')
    if selected_items_str:
        item_ids = selected_items_str.split(',')
        items_to_return = order.items.filter(id__in=item_ids, item_status='active')
    else:
        items_to_return = order.items.filter(item_status='active')
        
    if not items_to_return.exists():
        messages.error(request, 'No active items available for return.')
        return redirect('order_details', order.id)

    addresses = Address.objects.filter(user=request.user)
    from apps.orders.utils import calculate_item_refund_amount
    refund_total = sum(float(calculate_item_refund_amount(order, item)) for item in items_to_return)
    context = {
        'order': order,
        'addresses': addresses,
        'items_to_return': items_to_return,
        'refund_total': refund_total
    }

    return render(request, 'user/orders/return_request.html', context)


# ─── Individual Item Cancel ───────────────────────────────────────────────────

@login_required(login_url='login')
def cancel_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )
    order = item.order

    # Only active items in a non-final order can be cancelled
    cancellable_order_statuses = ['pending', 'processing']
    if item.item_status == 'active' and order.order_status in cancellable_order_statuses:
        item.item_status = 'cancelled'
        item.save()

        variant = item.product_variant
        variant.stock += item.quantity
        variant.save()

        cancelling_last_item = (order.items.filter(item_status='active').count() == 0)

        if cancelling_last_item:
            deduction_float = float(order.total_amount)
            order.total_amount = 0
            order.order_status = 'cancelled'
        else:
            from apps.orders.utils import calculate_item_refund_amount
            deduction_decimal = calculate_item_refund_amount(order, item)
            deduction_float = float(deduction_decimal)
            
            order.total_amount = float(order.total_amount) - deduction_float

            if order.total_amount < 0:
                order.total_amount = 0

        order.save()

        # Wallet refund for paid orders
        if order.payment_status == 'paid' and order.payment_method in ['Wallet', 'Razorpay']:
            from apps.payments.models import Wallet, WalletTransaction
            from decimal import Decimal
            refund_amount = Decimal(str(round(deduction_float, 2)))
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += refund_amount
            wallet.save()
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=refund_amount,
                transaction_type='credit',
                description=f'Refund for cancelled item in Order #{order.id}'
            )

        messages.success(request, 'Item cancelled successfully.')
    else:
        messages.error(request, 'This item cannot be cancelled.')

    return redirect('order_details', order_id=order.id)


# ─── Individual Item Return ───────────────────────────────────────────────────

@login_required(login_url='login')
def return_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )
    order = item.order

    # Only active items in a delivered / partially-returned order can be returned
    returnable_order_statuses = ['delivered', 'return_requested']
    if order.order_status not in returnable_order_statuses or item.item_status != 'active':
        messages.error(request, 'This item cannot be returned.')
        return redirect('order_details', order_id=order.id)

    if request.method == 'POST':
        return_type  = request.POST.get('return_type')
        reason       = request.POST.get('reason')
        comments     = request.POST.get('comments', '')
        refund_mode  = request.POST.get('refund_mode')
        address_id   = request.POST.get('pickup_address')
        images       = request.FILES.getlist('images')

        live_pickup = get_object_or_404(Address, id=address_id, user=request.user)
        pickup_address = OrderAddress.from_address(live_pickup)

        from apps.orders.utils import calculate_item_refund_amount
        return_request = Return.objects.create(
            order=order,
            order_item=item,
            user=request.user,
            return_type=return_type,
            reason=reason,
            comments=comments,
            refund_mode=refund_mode,
            pickup_address=pickup_address,
            refund_amount=calculate_item_refund_amount(order, item)
        )

        for image in images:
            ReturnImage.objects.create(return_request=return_request, image=image)

        item.item_status = 'return_requested'
        item.save()

        # Always update order status so user-side badge & tracking show immediately
        order.order_status = 'return_requested'
        order.save()

        messages.success(request, 'Return request submitted for item.')
        return redirect('order_details', order_id=order.id)

    return redirect('order_details', order_id=order.id)





