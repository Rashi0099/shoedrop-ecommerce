from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from itertools import chain

from apps.category.models import Category, SubCategory


@staff_member_required(login_url='admin_login')
def category_list(request):
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '')
    status_filter = request.GET.get('status', '')

    subcategories_queryset = SubCategory.objects.select_related('category')

    if search:
        subcategories_queryset = subcategories_queryset.filter(
            Q(name__icontains=search) | Q(category__name__icontains=search)
        )

    if status_filter == 'active':
        subcategories_queryset = subcategories_queryset.filter(is_active=True)
    elif status_filter == 'inactive':
        subcategories_queryset = subcategories_queryset.filter(is_active=False)

    # Sorting logic
    if sort == 'category':
        subcategories_queryset = subcategories_queryset.order_by('category__name', 'name')
    elif sort == '-category':
        subcategories_queryset = subcategories_queryset.order_by('-category__name', 'name')
    elif sort == 'subcategory':
        subcategories_queryset = subcategories_queryset.order_by('name')
    elif sort == '-subcategory':
        subcategories_queryset = subcategories_queryset.order_by('-name')
    elif sort == 'status':
        subcategories_queryset = subcategories_queryset.order_by('-is_active', 'category__name')
    elif sort == '-status':
        subcategories_queryset = subcategories_queryset.order_by('is_active', 'category__name')
    else:
        # Default sort
        subcategories_queryset = subcategories_queryset.order_by('category__name', 'name')

    combined_list = list(subcategories_queryset)
    total_count = len(combined_list)

    paginator = Paginator(combined_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': page_obj,
        'total_categories': total_count,
        'search': search,
        'sort': sort,
        'status_filter': status_filter
    }

    return render(
        request,
        'admin/category/category_list.html',
        context
    )


@staff_member_required(login_url='admin_login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        is_active = request.POST.get('is_active') == 'True'

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('add_category')

        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Category "{name}" already exists.')
            return redirect('add_category')

        Category.objects.create(
            name=name,
            is_active=is_active
        )

        messages.success(request, f'Category "{name}" added successfully.')
        return redirect('category_list')

    return render(
        request,
        'admin/category/add_category.html'
    )


@staff_member_required(login_url='admin_login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        is_active = request.POST.get('is_active') == 'True'

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('edit_category', category_id=category.id)

        if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            messages.error(request, f'Category "{name}" already exists.')
            return redirect('edit_category', category_id=category.id)

        category.name = name
        category.is_active = is_active
        category.save()

        # If a category is deactivated, also deactivate its subcategories
        if not is_active:
            SubCategory.objects.filter(category=category).update(is_active=False)

        messages.success(request, f'Category "{name}" updated successfully.')
        return redirect('category_list')

    context = {
        'category': category
    }

    return render(
        request,
        'admin/category/edit_category.html',
        context
    )


@staff_member_required(login_url='admin_login')
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # Soft delete — just mark as inactive, do not remove from database
    category.is_active = False
    category.save()

    # Also deactivate all subcategories under this category
    SubCategory.objects.filter(category=category).update(is_active=False)

    messages.success(request, f'Category "{category.name}" has been deactivated.')
    return redirect('category_list')


@staff_member_required(login_url='admin_login')
def add_subcategory(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('parent_id')
        is_active = request.POST.get('is_active') == 'True'

        if not name:
            messages.error(request, 'Subcategory name is required.')
            return redirect('add_subcategory')

        if not category_id:
            messages.error(request, 'Parent category is required.')
            return redirect('add_subcategory')

        category = get_object_or_404(Category, id=category_id)

        if SubCategory.objects.filter(name__iexact=name, category=category).exists():
            messages.error(request, f'Subcategory "{name}" already exists under this category.')
            return redirect('add_subcategory')

        SubCategory.objects.create(
            name=name,
            category=category,
            is_active=is_active
        )

        messages.success(request, f'Subcategory "{name}" added successfully.')
        return redirect('category_list')

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        'admin/category/add_subcategory.html',
        {
            'categories': categories
        }
    )


@staff_member_required(login_url='admin_login')
def edit_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('parent_id')
        is_active = request.POST.get('is_active') == 'True'

        if not name:
            messages.error(request, 'Subcategory name is required.')
            return redirect('edit_subcategory', subcategory_id=subcategory.id)

        if not category_id:
            messages.error(request, 'Parent category is required.')
            return redirect('edit_subcategory', subcategory_id=subcategory.id)

        category = get_object_or_404(Category, id=category_id)

        if SubCategory.objects.filter(name__iexact=name, category=category).exclude(id=subcategory.id).exists():
            messages.error(request, f'Subcategory "{name}" already exists under this category.')
            return redirect('edit_subcategory', subcategory_id=subcategory.id)

        subcategory.name = name
        subcategory.category = category
        subcategory.is_active = is_active
        subcategory.save()

        messages.success(request, f'Subcategory "{name}" updated successfully.')
        return redirect('category_list')

    # Allow current parent category even if inactive
    categories = Category.objects.filter(Q(is_active=True) | Q(id=subcategory.category_id))

    context = {
        'subcategory': subcategory,
        'categories': categories
    }

    return render(
        request,
        'admin/category/edit_subcategory.html',
        context
    )


@staff_member_required(login_url='admin_login')
def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # Soft delete — just mark as inactive
    subcategory.is_active = False
    subcategory.save()

    messages.success(request, f'Subcategory "{subcategory.name}" has been deactivated.')
    return redirect('category_list')