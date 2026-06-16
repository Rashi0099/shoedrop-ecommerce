from django.shortcuts import render
from apps.products.models import Product,ProductVariant

from django.shortcuts import (
    render,
    get_object_or_404
)
from apps.category.models import (
    Category,
    SubCategory
)

def shop(request):

    products = Product.objects.filter(
        is_active=True
    ).prefetch_related(
        'variants__images'
    )

    categories = Category.objects.filter(
        is_active=True
    )

    subcategories = SubCategory.objects.filter(
        is_active=True
    ).values_list('name', flat=True).distinct()

    sizes = ProductVariant.objects.filter(
        is_active=True
    ).values_list(
        'size',
        flat=True
    ).distinct()

    colors = ProductVariant.objects.filter(
        is_active=True
    ).values_list(
        'color',
        flat=True
    ).distinct()

    search = request.GET.get(
        'q'
    )

    category = request.GET.get(
        'category'
    )

    subcategory = request.GET.get(
        'subcategory'
    )

    size = request.GET.get(
        'size'
    )

    color = request.GET.get(
        'color'
    )

    sort = request.GET.get(
        'sort'
    )

    if search:

        products = products.filter(
            product_name__icontains=search
        )

    if category:

        if category.isdigit():
            products = products.filter(
                category_id=category
            )
            subcategories = subcategories.filter(
                category_id=category
            )
        else:
            products = products.filter(
                category__name__iexact=category
            )
            subcategories = subcategories.filter(
                category__name__iexact=category
            )

    if subcategory:
        if subcategory.isdigit():
            products = products.filter(
                subcategory_id=subcategory
            )
        else:
            products = products.filter(
                subcategory__name__iexact=subcategory
            )

    if size:

        products = products.filter(
            variants__size=size,
            variants__is_active=True
        )

    if color:

        products = products.filter(
            variants__color=color,
            variants__is_active=True
        )

    if sort == 'price_low':

        products = products.order_by(
            'variants__price'
        )

    elif sort == 'price_high':

        products = products.order_by(
            '-variants__price'
        )

    else:

        products = products.order_by(
            '-created_at'
        )

    products = products.distinct()

    context = {
        'products': products,
        'categories': categories,
        'subcategories': subcategories,
        'sizes': sizes,
        'colors': colors,
    }

    return render(
        request,
        'user/products/shop.html',
        context
    )


def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    variants = ProductVariant.objects.filter(
        product=product,
        is_active=True
    ).prefetch_related(
        'images'
    )

    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')

    selected_variant = variants.first()

    if selected_color and selected_size:
        v = variants.filter(color=selected_color, size=selected_size).first()
        if v:
            selected_variant = v
        else:
            # If the specific combo doesn't exist, fallback to just color or size
            v_color = variants.filter(color=selected_color).first()
            if v_color:
                selected_variant = v_color
            else:
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

    colors = variants.values_list(
        'color',
        flat=True
    ).distinct()

    sizes = variants.values_list(
        'size',
        flat=True
    ).distinct()

    # Pass the actual selected color and size so the UI knows what is active
    current_color = selected_variant.color if selected_variant else None
    current_size = selected_variant.size if selected_variant else None

    return render(
        request,
        'user/products/product_detail.html',
        {
            'product': product,
            'variants': variants,
            'selected_variant': selected_variant,
            'colors': colors,
            'sizes': sizes,
            'current_color': current_color,
            'current_size': current_size,
        }
    )