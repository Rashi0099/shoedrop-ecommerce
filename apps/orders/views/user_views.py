from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.addresses.models import Address
from apps.cart.models import CartItem
from apps.products.models import ProductVariant
from apps.orders.models import Order, OrderItem
from django.contrib import messages

@login_required(login_url='login')
def checkout(request):

    user_addresses = Address.objects.filter(user=request.user)

    checkout_items = []

    subtotal = 0

    buy_now_id = request.GET.get('buy_now')

    if buy_now_id:

        variant = get_object_or_404(ProductVariant, id=buy_now_id)

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

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'orders': orders
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

    context = {

        'order': order,

        'order_items': order_items

    }

    return render(

        request,

        'user/orders/order_details.html',

        context

    )

@login_required(login_url='login')
def return_order(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user

    )

    if order.order_status != 'delivered':

        return redirect(
            'order_details',
            order.id
        )

    order.order_status = 'return_requested'

    order.save()

    return redirect(
        'order_details',
        order.id
    )