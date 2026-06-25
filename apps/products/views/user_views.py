from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from apps.products.models import Product, ProductVariant
from apps.category.models import Category, SubCategory


def shop(request):

    products = Product.objects.filter(
        is_active=True,
        is_deleted=False
    ).prefetch_related('variants__images')

    categories = Category.objects.filter(is_active=True)

    subcategory_qs = SubCategory.objects.filter(is_active=True)

    sizes = ProductVariant.objects.filter(
        is_active=True
    ).values_list('size', flat=True).distinct()

    colors = ProductVariant.objects.filter(
        is_active=True
    ).values_list('color', flat=True).distinct()

    search = request.GET.get('q')
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    size = request.GET.get('size')
    color = request.GET.get('color')
    sort = request.GET.get('sort')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search:
        products = products.filter(product_name__icontains=search)

    if category:
        if category.isdigit():
            products = products.filter(category_id=category)
            subcategory_qs = subcategory_qs.filter(category_id=category)
        else:
            products = products.filter(category__name__iexact=category)
            subcategory_qs = subcategory_qs.filter(category__name__iexact=category)

    if subcategory:
        if subcategory.isdigit():
            products = products.filter(subcategory_id=subcategory)
        else:
            products = products.filter(subcategory__name__iexact=subcategory)

    if size:
        products = products.filter(variants__size=size, variants__is_active=True)

    if color:
        products = products.filter(variants__color=color, variants__is_active=True)

    if sort == 'price_low':
        products = products.order_by('variants__price')
    elif sort == 'price_high':
        products = products.order_by('-variants__price')
    elif sort == 'name_az':
        products = products.order_by('product_name')
    elif sort == 'name_za':
        products = products.order_by('-product_name')
    else:
        products = products.order_by('-created_at')

    products = products.distinct()

    subcategories = subcategory_qs.values_list('name', flat=True).distinct()

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Build set of variant IDs in the current user's wishlist for icon highlighting
    wishlist_variant_ids = set()
    if request.user.is_authenticated:
        from apps.wishlist.models import WishlistItem
        wishlist_variant_ids = set(
            WishlistItem.objects.filter(user=request.user)
            .values_list('variant_id', flat=True)
        )

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'subcategories': subcategories,
        'sizes': sizes,
        'colors': colors,
        'wishlist_variant_ids': wishlist_variant_ids,
    }

    return render(request, 'user/products/shop.html', context)


def product_detail(request, product_id):

    try:
        product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
    except Product.DoesNotExist:
        messages.error(request, 'This product is not available.')
        return redirect('shop')

    variants = ProductVariant.objects.filter(
        product=product,
        is_active=True
    ).prefetch_related('images')

    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')

    selected_variant = variants.first()

    if selected_color and selected_size:
        v = variants.filter(color=selected_color, size=selected_size).first()
        if v:
            selected_variant = v
        else:
            # Fallback: try matching by color only
            v_color = variants.filter(color=selected_color).first()
            if v_color:
                selected_variant = v_color
            else:
                # Fallback: try matching by size only
                v_size = variants.filter(size=selected_size).first()
                if v_size:
                    selected_variant = v_size

    elif selected_color:
        v = variants.filter(color=selected_color).first()
        if v:
            selected_variant = v

    elif selected_size:
        v = variants.filter(size=selected_size).first()
        if v:
            selected_variant = v

    colors = variants.values_list('color', flat=True).distinct()
    sizes = variants.values_list('size', flat=True).distinct()

    current_color = selected_variant.color if selected_variant else None
    current_size = selected_variant.size if selected_variant else None

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        is_deleted=False
    ).exclude(id=product.id).prefetch_related('variants__images')[:4]

    return render(request, 'user/products/product_detail.html', {
        'product': product,
        'variants': variants,
        'selected_variant': selected_variant,
        'colors': colors,
        'sizes': sizes,
        'current_color': current_color,
        'current_size': current_size,
        'related_products': related_products,
    })