from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.wishlist.models import WishlistItem
from apps.products.models import ProductVariant


@login_required(login_url='login')
def wishlist_view(request):

    wishlist_items = WishlistItem.objects.filter(
        user=request.user
    ).select_related('variant__product').prefetch_related('variant__images')

    context = {
        'wishlist_items': wishlist_items,
    }

    return render(request, 'user/wishlist/wishlist.html', context)


@login_required(login_url='login')
def add_to_wishlist(request, variant_id):

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if not variant.product.is_active or not variant.is_active:
        messages.error(request, 'This product is not available.')
        return redirect('shop')

    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        variant=variant
    )

    if created:
        messages.success(request, 'Item added to wishlist.')
    else:
        messages.info(request, 'This item is already in your wishlist.')

    return redirect('wishlist')


@login_required(login_url='login')
def remove_from_wishlist(request, item_id):

    wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    wishlist_item.delete()

    messages.success(request, 'Item removed from wishlist.')
    return redirect('wishlist')
