from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.addresses.models import Address
from apps.cart.models import CartItem
from apps.products.models import ProductVariant

@login_required(login_url='login')
def checkout(request):
    
    user_addresses = Address.objects.filter(user=request.user)
    
    checkout_items = []
    subtotal = 0
    
    buy_now_id = request.GET.get('buy_now')
    
    if buy_now_id:
     
        variant = ProductVariant.objects.get(id=buy_now_id)
        
        item_data = {
            'variant': variant,
            'quantity': 1,
            'get_total_price': variant.price
        }
        
        checkout_items.append(item_data)
        subtotal = variant.price
        
    else:
        
        cart_items_from_db = CartItem.objects.filter(user=request.user)
        
        if not cart_items_from_db:
            return redirect('shop')
            
        for item in cart_items_from_db:
            item_data = {
                'variant': item.variant,
                'quantity': item.quantity,
                'get_total_price': item.get_total_price()
            }
            checkout_items.append(item_data)
            
            subtotal = subtotal + item.get_total_price()
            
            
    gst_amount = float(subtotal) * 0.18   # 18% GST
    delivery_fee = 0                      # Free delivery
    
    final_grand_total = float(subtotal) + gst_amount + delivery_fee

    context = {
        'addresses': user_addresses,
        'cart_items': checkout_items,    
        'subtotal': subtotal,
        'gst': round(gst_amount, 2),      #
        'delivery_charges': delivery_fee,
        'grand_total': round(final_grand_total, 2),
    }
    
    return render(request, 'user/orders/checkout.html', context)

@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        
        
        return redirect('shop') 
        
    return redirect('checkout')
