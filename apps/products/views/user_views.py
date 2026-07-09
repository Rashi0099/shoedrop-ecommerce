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

    from django.db.models import Min, Max
    if sort == 'price_low':
        products = products.annotate(min_price=Min('variants__price')).order_by('min_price')
    elif sort == 'price_high':
        products = products.annotate(max_price=Max('variants__price')).order_by('-max_price')
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

    from apps.reviews.models import Review
    from apps.orders.models import OrderItem
    from django.db.models import Avg, Count

    reviews = Review.objects.filter(product=product, is_active=True).select_related('user')

    # Rating stats
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = reviews.count()
    rating_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}

    # Check if logged-in user has purchased this product (for verified review badge)
    user_has_purchased = False
    user_existing_review = None
    if request.user.is_authenticated:
        user_has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product_variant__product=product,
            order__order_status='delivered'
        ).exists()
        user_existing_review = reviews.filter(user=request.user).first()

    return render(request, 'user/products/product_detail.html', {
        'product': product,
        'variants': variants,
        'selected_variant': selected_variant,
        'colors': colors,
        'sizes': sizes,
        'current_color': current_color,
        'current_size': current_size,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'rating_counts': rating_counts,
        'user_has_purchased': user_has_purchased,
        'user_existing_review': user_existing_review,
    })