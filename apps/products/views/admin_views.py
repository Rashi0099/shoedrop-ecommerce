from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from apps.products.models import Product, ProductVariant, VariantImage
from apps.category.models import Category, SubCategory


@staff_member_required(login_url='admin_login')
def product_list(request):
    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')

    products = Product.objects.select_related('category', 'subcategory')

    if search:
        products = products.filter(product_name__icontains=search)

    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)

    if category_id:
        products = products.filter(category_id=category_id)

    if subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)

    products = products.order_by('-created_at')
    total_products = products.count()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'search': search,
        'status': status,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'total_products': total_products,
        'categories': Category.objects.filter(is_active=True),
        'subcategories': SubCategory.objects.filter(is_active=True),
    }

    return render(request, 'admin/products/product_list.html', context)


@staff_member_required(login_url='admin_login')
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name', '').strip()
        description = request.POST.get('description', '').strip()
        product_features = request.POST.get('features', '').strip()
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')

        if not product_name:
            messages.error(request, 'Product name is required.')
            return redirect('add_product')

        if len(product_name) < 3:
            messages.error(request, 'Product name must be at least 3 characters long.')
            return redirect('add_product')

        if not description:
            messages.error(request, 'Product description is required.')
            return redirect('add_product')

        if Product.objects.filter(product_name__iexact=product_name).exists():
            messages.error(request, f'Product "{product_name}" already exists.')
            return redirect('add_product')

        if not category_id or not subcategory_id:
            messages.error(request, 'Category and subcategory are required.')
            return redirect('add_product')

        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)

        if subcategory.category != category:
            messages.error(request, 'Invalid subcategory for selected category.')
            return redirect('add_product')

        Product.objects.create(
            product_name=product_name,
            description=description,
            category=category,
            subcategory=subcategory,
            product_features=product_features
        )

        messages.success(request, f'Product "{product_name}" added successfully.')
        return redirect('product_list')

    context = {
        'categories': Category.objects.filter(is_active=True),
        'subcategories': SubCategory.objects.filter(is_active=True),
    }

    return render(request, 'admin/products/add_product.html', context)


@staff_member_required(login_url='admin_login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = request.POST.get('product_name', '').strip()
        description = request.POST.get('description', '').strip()
        product_features = request.POST.get('features', '').strip()
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')

        if not product_name:
            messages.error(request, 'Product name is required.')
            return redirect('edit_product', product_id=product.id)

        if len(product_name) < 3:
            messages.error(request, 'Product name must be at least 3 characters long.')
            return redirect('edit_product', product_id=product.id)

        if not description:
            messages.error(request, 'Product description is required.')
            return redirect('edit_product', product_id=product.id)

        if Product.objects.filter(product_name__iexact=product_name).exclude(id=product.id).exists():
            messages.error(request, f'Product "{product_name}" already exists.')
            return redirect('edit_product', product_id=product.id)

        if not category_id or not subcategory_id:
            messages.error(request, 'Category and subcategory are required.')
            return redirect('edit_product', product_id=product.id)

        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)

        if subcategory.category != category:
            messages.error(request, 'Invalid subcategory for selected category.')
            return redirect('edit_product', product_id=product.id)

        product.product_name = product_name
        product.description = description
        product.product_features = product_features
        product.category = category
        product.subcategory = subcategory
        product.save()

        messages.success(request, f'Product "{product_name}" updated successfully.')
        return redirect('product_list')

    categories = Category.objects.filter(Q(is_active=True) | Q(id=product.category_id))
    subcategories = SubCategory.objects.filter(
        Q(is_active=True) | Q(id=product.subcategory_id)
    )

    context = {
        'product': product,
        'categories': categories,
        'subcategories': subcategories,
    }

    return render(request, 'admin/products/edit_product.html', context)


@staff_member_required(login_url='admin_login')
def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()

    status_label = 'listed' if product.is_active else 'unlisted'
    messages.success(request, f'"{product.product_name}" is now {status_label}.')
    return redirect('product_list')


@staff_member_required(login_url='admin_login')
def variant_list(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product).order_by('-created_at')

    context = {
        'product': product,
        'variants': variants,
    }

    return render(request, 'admin/products/variant_list.html', context)


@staff_member_required(login_url='admin_login')
def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        size = request.POST.get('size', '').strip()
        color = request.POST.get('color', '').strip()
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active') == 'True'

        if not all([size, color, price, stock]):
            messages.error(request, 'All fields are required.')
            return redirect('add_variant', product_id=product.id)

        try:
            price = float(price)
            if price <= 0:
                messages.error(request, 'Price must be greater than zero.')
                return redirect('add_variant', product_id=product.id)
        except ValueError:
            messages.error(request, 'Invalid price format.')
            return redirect('add_variant', product_id=product.id)

        try:
            stock = int(stock)
            if stock < 0:
                messages.error(request, 'Stock cannot be negative.')
                return redirect('add_variant', product_id=product.id)
        except ValueError:
            messages.error(request, 'Invalid stock format.')
            return redirect('add_variant', product_id=product.id)

        images = request.FILES.getlist('images')

        if len(images) < 3:
            messages.error(request, 'Please upload at least 3 images for this variant.')
            return redirect('add_variant', product_id=product.id)

        variant = ProductVariant.objects.create(
            product=product,
            size=size,
            color=color,
            price=price,
            stock=stock,
            is_active=is_active
        )

        for i, image_file in enumerate(images):
            VariantImage.objects.create(
                variant=variant,
                image=image_file,
                is_primary=(i == 0)
            )

        messages.success(request, 'Variant added successfully.')
        return redirect('variant_list', product_id=product.id)

    return render(request, 'admin/products/add_variant.html', {'product': product})


@staff_member_required(login_url='admin_login')
def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product

    if request.method == 'POST':
        size = request.POST.get('size', '').strip()
        color = request.POST.get('color', '').strip()
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active') == 'True'

        if not all([size, color, price, stock]):
            messages.error(request, 'All fields are required.')
            return redirect('edit_variant', variant_id=variant.id)

        try:
            price = float(price)
            if price <= 0:
                messages.error(request, 'Price must be greater than zero.')
                return redirect('edit_variant', variant_id=variant.id)
        except ValueError:
            messages.error(request, 'Invalid price format.')
            return redirect('edit_variant', variant_id=variant.id)

        try:
            stock = int(stock)
            if stock < 0:
                messages.error(request, 'Stock cannot be negative.')
                return redirect('edit_variant', variant_id=variant.id)
        except ValueError:
            messages.error(request, 'Invalid stock format.')
            return redirect('edit_variant', variant_id=variant.id)

        variant.size = size
        variant.color = color
        variant.price = price
        variant.stock = stock
        variant.is_active = is_active
        variant.save()

        images = request.FILES.getlist('images')
        if images:
            if len(images) < 3:
                messages.error(request, 'Please upload at least 3 images if adding new images.')
                return redirect('edit_variant', variant_id=variant.id)

            has_existing = variant.images.exists()
            for i, image_file in enumerate(images):
                VariantImage.objects.create(
                    variant=variant,
                    image=image_file,
                    is_primary=(i == 0 and not has_existing)
                )

        messages.success(request, 'Variant updated successfully.')
        return redirect('variant_list', product_id=product.id)

    context = {
        'variant': variant,
        'product': product,
    }

    return render(request, 'admin/products/edit_variant.html', context)


@staff_member_required(login_url='admin_login')
def delete_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product_id = variant.product.id
    variant.delete()
    messages.success(request, 'Variant deleted successfully.')
    return redirect('variant_list', product_id=product_id)


@staff_member_required(login_url='admin_login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_name = product.product_name
    product.delete()
    messages.success(request, f'Product "{product_name}" deleted successfully.')
    return redirect('product_list')