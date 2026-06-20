from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from apps.addresses.models import Address
from apps.cart.models import CartItem
from apps.products.models import ProductVariant
from apps.orders.models import Order, OrderItem

@login_required(login_url='login')
def checkout(request):
    # 1. Fetch saved addresses for the logged-in user
    user_addresses = Address.objects.filter(user=request.user)
    
    checkout_items = []
    subtotal = 0
    
    # Check if the user is buying a single product directly
    buy_now_id = request.GET.get('buy_now')
    
    if buy_now_id:
        # Get the specific product variant
        variant = get_object_or_404(ProductVariant, id=buy_now_id)
        
        # Create a dictionary representing the item
        item_data = {
            'variant': variant,
            'quantity': 1,
            'get_total_price': variant.price
        }
        checkout_items.append(item_data)
        subtotal = variant.price
    else:
        # Get all items in the user's cart
        cart_items_from_db = CartItem.objects.filter(user=request.user)
        
        # Redirect to shop if the cart is empty
        if not cart_items_from_db.exists():
            return redirect('shop')
            
        for item in cart_items_from_db:
            item_data = {
                'variant': item.variant,
                'quantity': item.quantity,
                'get_total_price': item.get_total_price()
            }
            checkout_items.append(item_data)
            subtotal += item.get_total_price()
            
    # Calculate totals
    gst_amount = float(subtotal) * 0.18  # 18% GST
    delivery_fee = 0                     # Free delivery
    grand_total = float(subtotal) + gst_amount + delivery_fee

    context = {
        'addresses': user_addresses,
        'cart_items': checkout_items,
        'subtotal': subtotal,
        'gst': round(gst_amount, 2),
        'delivery_charges': delivery_fee,
        'grand_total': round(grand_total, 2),
    }
    return render(request, 'user/orders/checkout.html', context)


@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        # Get the selected address and variant from the form
        address_id = request.POST.get('address_id')
        buy_now_id = request.POST.get('buy_now')
        
        # Validation: Check if address is selected
        if not address_id:
            return redirect('checkout')
            
        # Get the address object
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Calculate subtotal and collect items
        order_items_to_create = []
        subtotal = 0
        
        if buy_now_id:
            # Single item purchase ("Buy Now")
            variant = get_object_or_404(ProductVariant, id=buy_now_id)
            order_items_to_create.append({
                'variant': variant,
                'quantity': 1,
                'price': variant.price
            })
            subtotal = variant.price
        else:
            # Cart checkout
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                return redirect('shop')
                
            for item in cart_items:
                order_items_to_create.append({
                    'variant': item.variant,
                    'quantity': item.quantity,
                    'price': item.variant.price
                })
                subtotal += item.get_total_price()
                
        # Calculate Grand Total
        gst_amount = float(subtotal) * 0.18
        grand_total = float(subtotal) + gst_amount
        
        # Get the payment method from the form
        payment_method = request.POST.get('payment_method')
        
        # Determine payment method to save in DB (mapping Razorpay to Card)
        db_payment_method = 'COD'
        if payment_method == 'wallet':
            db_payment_method = 'Wallet'
        elif payment_method == 'razorpay':
            db_payment_method = 'Card'

        # Create the Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method=db_payment_method,
            payment_status='pending',
            order_status='pending',
            total_amount=round(grand_total, 2)
        )
        
        # Create the OrderItems & update product variant stocks
        for item in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                product_variant=item['variant'],
                quantity=item['quantity'],
                unit_price=item['price']
            )
            
            # Decrement variant stock
            variant = item['variant']
            if variant.stock >= item['quantity']:
                variant.stock -= item['quantity']
                variant.save()
            
        # Clear the cart (only for cart checkout)
        if not buy_now_id:
            CartItem.objects.filter(user=request.user).delete()
            
        # Redirect to the success page
        return redirect(reverse('success_order') + f'?order_id={order.id}')
        
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
            
    context = {
        'order': order
    }
    return render(request, 'user/orders/order_success.html', context)

    