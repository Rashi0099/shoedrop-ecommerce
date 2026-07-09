from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.coupons.models import Coupon
from apps.category.models import Category


@login_required(login_url='admin_login')
def coupon_list(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    coupons = Coupon.objects.all().order_by('-created_at')

    if search:
        coupons = coupons.filter(coupon_name__icontains=search) | coupons.filter(coupon_code__icontains=search)

    if status == 'active':
        coupons = coupons.filter(is_active=True)
    elif status == 'inactive':
        coupons = coupons.filter(is_active=False)

    context = {
        'coupons': coupons,
        'search': search,
        'status_filter': status,
    }
    return render(request, 'admin/coupons/coupon_list.html', context)


@login_required(login_url='admin_login')
def add_coupon(request):
    if request.method == 'POST':
        coupon_name = request.POST.get('coupon_name')
        coupon_code = request.POST.get('coupon_code', '').upper()
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        min_cart_value = request.POST.get('min_cart_value') or 0
        usage_limit = request.POST.get('usage_limit') or 1
        category_id = request.POST.get('applicable_category')
        valid_from = request.POST.get('valid_from')
        valid_till = request.POST.get('valid_till')

        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            messages.error(request, 'Coupon code already exists.')
            return redirect('add_coupon')

        applicable_category = None
        if category_id:
            applicable_category = Category.objects.filter(id=category_id).first()

        Coupon.objects.create(
            coupon_name=coupon_name,
            coupon_code=coupon_code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_cart_value=min_cart_value,
            usage_limit=usage_limit,
            applicable_category=applicable_category,
            valid_from=valid_from if valid_from else None,
            valid_till=valid_till if valid_till else None,
            is_active=True
        )
        messages.success(request, 'Coupon created successfully.')
        return redirect('coupon_list')

    categories = Category.objects.all()
    return render(request, 'admin/coupons/add_coupon.html', {'categories': categories})


@login_required(login_url='admin_login')
def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == 'POST':
        new_code = request.POST.get('coupon_code', '').upper()
        if new_code != coupon.coupon_code and Coupon.objects.filter(coupon_code=new_code).exists():
            messages.error(request, 'Coupon code already exists.')
            return redirect('edit_coupon', coupon_id=coupon.id)

        coupon.coupon_name = request.POST.get('coupon_name')
        coupon.coupon_code = new_code
        coupon.discount_type = request.POST.get('discount_type')
        coupon.discount_value = request.POST.get('discount_value')
        coupon.min_cart_value = request.POST.get('min_cart_value') or 0
        coupon.usage_limit = request.POST.get('usage_limit') or 1
        coupon.is_active = request.POST.get('is_active') == 'on'

        category_id = request.POST.get('applicable_category')
        coupon.applicable_category = Category.objects.filter(id=category_id).first() if category_id else None

        valid_from = request.POST.get('valid_from')
        valid_till = request.POST.get('valid_till')
        coupon.valid_from = valid_from if valid_from else None
        coupon.valid_till = valid_till if valid_till else None

        coupon.save()
        messages.success(request, 'Coupon updated successfully.')
        return redirect('coupon_list')

    categories = Category.objects.all()
    valid_from_str = coupon.valid_from.strftime('%Y-%m-%dT%H:%M') if coupon.valid_from else ''
    valid_till_str = coupon.valid_till.strftime('%Y-%m-%dT%H:%M') if coupon.valid_till else ''

    context = {
        'coupon': coupon,
        'categories': categories,
        'valid_from_str': valid_from_str,
        'valid_till_str': valid_till_str,
    }
    return render(request, 'admin/coupons/edit_coupon.html', context)


@login_required(login_url='admin_login')
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully.')
    return redirect('coupon_list')
