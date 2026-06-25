from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.addresses.models import Address
from apps.cart.models import CartItem
from apps.products.models import ProductVariant
from apps.orders.models import Order, OrderItem
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

        if variant.stock < 1:
            messages.error(request, 'Sorry, this item is currently out of stock.')
            return redirect('shop')

        checkout_items.append({
            'variant': variant,
            'quantity': 1,
            'get_total_price': variant.price
        })

        subtotal = variant.price

    else:

        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('shop')

        for item in cart_items:

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

    grand_total = float(subtotal) + gst + delivery_fee

    context = {
        'addresses': user_addresses,
        'cart_items': checkout_items,
        'subtotal': subtotal,
        'gst': round(gst, 2),
        'delivery_charges': delivery_fee,
        'grand_total': round(grand_total, 2)
    }

    return render(request, 'user/orders/checkout.html', context)

@login_required(login_url='login')
def place_order(request):

    if request.method != 'POST':
        return redirect('checkout')

    payment_method = request.POST.get('payment_method')

   

    if not payment_method:
        messages.error(request,'pls select any payment method')
        return render(request,'user/orders/checkout.html')

    if payment_method == 'cod':
        return cod_order(request)

    elif payment_method == 'wallet':
        return wallet_payment(request)

    elif payment_method == 'razorpay':
        return razorpay_payment(request)

    return redirect('checkout')



@login_required(login_url='login')
def cod_order(request):


    address_id = request.POST.get('address_id')

    buy_now_id = request.POST.get('buy_now')

    if not address_id:
        return redirect('checkout')

    address = get_object_or_404(Address, id=address_id, user=request.user)

    subtotal = 0

    order_items = []

    if buy_now_id:

        variant = get_object_or_404(ProductVariant, id=buy_now_id)

        if variant.stock < 1:
            return redirect('checkout')

        order_items.append({
            'variant': variant,
            'quantity': 1,
            'price': variant.price
        })

        subtotal = variant.price

    else:

        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('shop')

        for item in cart_items:

            if item.variant.stock < item.quantity:
                return redirect('checkout')

            order_items.append({
                'variant': item.variant,
                'quantity': item.quantity,
                'price': item.variant.price
            })

            subtotal += item.get_total_price()

    gst = float(subtotal) * 0.18

    grand_total = float(subtotal) + gst

    order = Order.objects.create(
        user=request.user,
        address=address,
        payment_method='COD',
        payment_status='pending',
        order_status='pending',
        total_amount=round(grand_total, 2)
    )

    for item in order_items:

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
    

    return redirect(f'/orders/order-success/?order_id={order.id}')


# Future
  

@login_required(login_url='login')
def wallet_payment(request):

   return redirect('checkout')

@login_required(login_url='login')
def razorpay_payment(request):

   return redirect('checkout')




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

    context = {
        'orders': orders,
        'search': search,
    }

    return render(
        request,
        'user/orders/order_list.html',
        context
    )

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
            
        for item in items_to_cancel:
            item.item_status = 'cancelled'
            item.save()
            
            # Restore stock
            variant = item.product_variant
            variant.stock += item.quantity
            variant.save()
            
            # Deduct from order total (including 18% GST)
            deduction = float(item.total) * 1.18
            order.total_amount = float(order.total_amount) - deduction
            
        # Ensure total_amount doesn't go below 0 (due to floating point issues or coupons)
        if order.total_amount < 0:
            order.total_amount = 0

        # If all items are cancelled, mark order as cancelled
        if not order.items.filter(item_status='active').exists():
            order.order_status = 'cancelled'
            order.total_amount = 0
            
        order.save()
            
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

        pickup_address = get_object_or_404(Address, id=address_id, user=request.user)

        items_to_return = order.items.filter(id__in=selected_item_ids, item_status='active')

        for item in items_to_return:
            return_request = Return.objects.create(
                order=order,
                order_item=item,
                user=request.user,
                return_type=return_type,
                reason=reason,
                comments=comments,
                refund_mode=refund_mode,
                pickup_address=pickup_address
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
    refund_total = sum(item.unit_price for item in items_to_return)
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

        # Deduct from order total (including 18% GST)
        deduction = float(item.total) * 1.18
        order.total_amount = float(order.total_amount) - deduction
        
        if order.total_amount < 0:
            order.total_amount = 0

        # If ALL items are now cancelled → cancel the whole order
        if not order.items.filter(item_status='active').exists():
            order.order_status = 'cancelled'
            order.total_amount = 0
            
        order.save()

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

        pickup_address = get_object_or_404(Address, id=address_id, user=request.user)

        return_request = Return.objects.create(
            order=order,
            order_item=item,
            user=request.user,
            return_type=return_type,
            reason=reason,
            comments=comments,
            refund_mode=refund_mode,
            pickup_address=pickup_address,
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