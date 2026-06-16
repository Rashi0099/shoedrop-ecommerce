from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.cart.models import CartItem
from apps.products.models import ProductVariant, Product
from apps.wishlist.models import WishlistItem

# Maximum items of one variant a user can add to cart
MAX_QUANTITY = 5


@login_required(login_url='login')
def cart_view(request):

    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related('variant__product')

    subtotal = sum(item.get_total_price() for item in cart_items)

    tax = round(subtotal * 10 / 100, 2)

    total = subtotal + tax

    suggested_products = Product.objects.filter(
        is_active=True
    ).exclude(
        variants__cartitem__user=request.user
    ).distinct()[:4]

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'suggested_products': suggested_products,
    }

    return render(request, 'user/cart/cart.html', context)


@login_required(login_url='login')
def add_to_cart(request, variant_id):

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if not variant.product.is_active or not variant.is_active:
        messages.error(request, 'Sorry, this product is not available.')
        return redirect('shop')

    if variant.stock <= 0:
        messages.error(request, 'Sorry, this item is currently out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'shop'))

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        variant=variant
    )

    if not created:
        # Item already in cart — check limits before increasing quantity
        if cart_item.quantity >= MAX_QUANTITY:
            messages.error(request, f'You can only add up to {MAX_QUANTITY} of this item.')
        elif cart_item.quantity < variant.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Item quantity updated in cart.')
        else:
            messages.error(request, f'Sorry, only {variant.stock} units are available in stock.')
    else:
        messages.success(request, 'Item added to cart.')

    WishlistItem.objects.filter(user=request.user, variant=variant).delete()

    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()

    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required(login_url='login')
def update_cart_quantity(request, item_id):

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        if cart_item.quantity >= MAX_QUANTITY:
            messages.error(request, f'Maximum limit of {MAX_QUANTITY} items reached.')
        elif cart_item.quantity < cart_item.variant.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, f'Sorry, only {cart_item.variant.stock} units are available in stock.')

    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # If quantity is 1 and user decreases, remove the item
            cart_item.delete()

    return redirect('cart')
