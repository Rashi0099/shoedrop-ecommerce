from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.wishlist.models import WishlistItem
from apps.products.models import ProductVariant


@login_required(login_url='login')
def wishlist_view(request):

    wishlist_items = WishlistItem.objects.filter(
        user=request.user,
        variant__product__is_deleted=False
    ).select_related('variant__product').prefetch_related('variant__images')

    context = {
        'wishlist_items': wishlist_items,
    }

    return render(request, 'user/wishlist/wishlist.html', context)


@login_required(login_url='login')
def add_to_wishlist(request, variant_id):

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if not variant.product.is_active or not variant.is_active or variant.product.is_deleted:
        messages.error(request, 'This product is not available.')
        return redirect('shop')

    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        variant=variant
    )

    if created:
        messages.success(request, 'Added to wishlist.')
    else:
        messages.info(request, 'Already in your wishlist.')

    # Go back to whichever page the user came from (shop, product detail, etc.)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('shop')


@login_required(login_url='login')
def remove_from_wishlist(request, item_id):

    wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    wishlist_item.delete()

    messages.success(request, 'Item removed from wishlist.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('wishlist')


@login_required(login_url='login')
def toggle_wishlist(request, variant_id):
    """Add to wishlist if not present, remove if already present. Always returns to referer."""
    variant = get_object_or_404(ProductVariant, id=variant_id)

    existing = WishlistItem.objects.filter(user=request.user, variant=variant).first()

    if existing:
        existing.delete()
        messages.success(request, 'Removed from wishlist.')
    else:
        if not variant.product.is_active or not variant.is_active or variant.product.is_deleted:
            messages.error(request, 'This product is not available.')
        else:
            WishlistItem.objects.create(user=request.user, variant=variant)
            messages.success(request, 'Added to wishlist.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('shop')
