from django.shortcuts import render, redirect

from django.contrib import messages

from django.contrib.auth import authenticate

from django.contrib.auth import login

from django.views.decorators.cache import never_cache

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import logout

from django.contrib.auth import update_session_auth_hash

from django.utils import timezone

from django.db.models import Sum, Count, Avg

from django.db.models.functions import TruncMonth

from apps.orders.models import Order, OrderItem

from apps.accounts.models import User

import json

from datetime import timedelta


@never_cache
def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:

        return redirect('admin_dashboard')

    if request.method == 'POST':

        email = request.POST.get('email').strip()

        password = request.POST.get('password')

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is not None and user.is_staff:

            login(request,user)

            return redirect('admin_dashboard')

        messages.error(request,'Invalid admin credentials')

    return render(request,'admin/accounts/login.html')



@staff_member_required(login_url='admin_login')
def admin_dashboard(request):
    from apps.products.models import Product
    from django.db.models import Sum, Avg
    from apps.orders.models import Order
    from apps.accounts.models import User
    from django.utils import timezone
    
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    today_orders = Order.objects.filter(created_at__date=today)
    today_paid_orders = today_orders.filter(payment_status='paid')
    
    orders_today = today_paid_orders.count()
    
    today_gross = today_paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_discount = today_paid_orders.aggregate(Sum('coupon_discount'))['coupon_discount__sum'] or 0
    revenue_today = today_gross - today_discount
    
    avg_order_today = today_paid_orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    refunds_today = today_orders.filter(order_status='returned').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    all_paid_orders = Order.objects.filter(payment_status='paid')
    
    orders_all = all_paid_orders.count()
    
    gross_all = all_paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    discount_all = all_paid_orders.aggregate(Sum('coupon_discount'))['coupon_discount__sum'] or 0
    net_all = gross_all - discount_all
    
    avg_order_all = all_paid_orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    refunds_all = Order.objects.filter(order_status='returned').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    customers_all = User.objects.filter(is_staff=False, is_superuser=False).count()
    products_all = Product.objects.count()
    
    month_paid_orders = Order.objects.filter(created_at__date__gte=first_day_of_month, payment_status='paid')
    month_gross = month_paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    month_discount = month_paid_orders.aggregate(Sum('coupon_discount'))['coupon_discount__sum'] or 0
    month_revenue = month_gross - month_discount
    
    pending_orders = Order.objects.filter(order_status='pending').count()
    delivered_orders = Order.objects.filter(order_status='delivered').count()
    
    top_seller_today = OrderItem.objects.filter(
        order__created_at__date=today,
        order__payment_status='paid'
    ).values(
        'product_variant__product__product_name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold').first()
    
    context = {
        'revenue_today': round(revenue_today, 2),
        'orders_today': orders_today,
        'refunds_today': round(refunds_today, 2),
        'avg_order_today': round(avg_order_today, 2),
        
        'gross_all': round(gross_all, 2),
        'discount_all': round(discount_all, 2),
        'net_all': round(net_all, 2),
        'refunds_all': round(refunds_all, 2),
        'avg_order_all': round(avg_order_all, 2),
        'orders_all': orders_all,
        'customers_all': customers_all,
        'products_all': products_all,
        
        'month_revenue': round(month_revenue, 2),
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'top_seller_today': top_seller_today,
    }

    return render(request, 'admin/accounts/dashboard.html', context)


@staff_member_required(login_url='admin_login')
def analytics_dashboard(request):
    

    now = timezone.now()
    today = now.date()
    period = request.GET.get('period', 'monthly')
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')

    if date_from_str and date_to_str:
        from datetime import datetime
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = today.replace(day=1)
            date_to = today
    elif period == 'daily':
        date_from = today
        date_to = today
    elif period == 'weekly':
        date_from = today - timedelta(days=6)
        date_to = today
    elif period == 'yearly':
        date_from = today.replace(month=1, day=1)
        date_to = today
    else:
        date_from = today.replace(day=1)
        date_to = today

    base_qs = Order.objects.filter(
        payment_status='paid',
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    )

    total_orders = base_qs.count()
    gross_revenue = base_qs.aggregate(s=Sum('total_amount'))['s'] or 0
    total_coupon_discount = base_qs.aggregate(s=Sum('coupon_discount'))['s'] or 0
    net_revenue = gross_revenue - total_coupon_discount
    avg_order_value = base_qs.aggregate(a=Avg('total_amount'))['a'] or 0

    returned_qs = Order.objects.filter(
        order_status='returned',
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    )
    total_refunds = returned_qs.aggregate(s=Sum('total_amount'))['s'] or 0

    new_customers = User.objects.filter(
        is_staff=False,
        date_joined__date__gte=date_from,
        date_joined__date__lte=date_to
    ).count()
    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()

    all_paid = Order.objects.filter(payment_status='paid')
    monthly_data = (
        all_paid.annotate(month=TruncMonth('created_at'))
        .values('month').annotate(revenue=Sum('total_amount'), orders=Count('id'))
        .order_by('month')
    )
    last_6 = list(monthly_data)[-6:]
    chart_labels = json.dumps([m['month'].strftime('%b %Y') for m in last_6])
    chart_revenue = json.dumps([float(m['revenue']) for m in last_6])
    chart_orders = json.dumps([m['orders'] for m in last_6])

    top_products = (
        OrderItem.objects.filter(
            order__payment_status='paid',
            order__created_at__date__gte=date_from,
            order__created_at__date__lte=date_to
        )
        .values('product_variant__product__product_name')
        .annotate(total_sold=Sum('quantity'), revenue=Sum('total'))
        .order_by('-total_sold')[:5]
    )

    cat_data = (
        OrderItem.objects.filter(
            order__payment_status='paid',
            order__created_at__date__gte=date_from,
            order__created_at__date__lte=date_to
        )
        .values('product_variant__product__category__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )
    max_cat = max((c['total_sold'] for c in cat_data), default=1) or 1
    top_categories = [
        {**c, 'pct': int(c['total_sold'] / max_cat * 100)}
        for c in cat_data
    ]

    status_counts = {
        'pending': base_qs.filter(order_status='pending').count(),
        'processing': base_qs.filter(order_status='processing').count(),
        'shipped': base_qs.filter(order_status='shipped').count(),
        'delivered': base_qs.filter(order_status='delivered').count(),
        'cancelled': Order.objects.filter(order_status='cancelled', payment_status='paid', created_at__date__gte=date_from, created_at__date__lte=date_to).count(),
    }

    payment_breakdown = (
        base_qs.values('payment_method')
        .annotate(count=Count('id'), revenue=Sum('total_amount'))
        .order_by('-count')
    )

    context = {
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'total_orders': total_orders,
        'gross_revenue': round(gross_revenue, 2),
        'net_revenue': round(net_revenue, 2),
        'avg_order_value': round(avg_order_value, 2),
        'total_coupon_discount': round(total_coupon_discount, 2),
        'total_refunds': round(total_refunds, 2),
        'new_customers': new_customers,
        'total_customers': total_customers,
        'chart_labels': chart_labels,
        'chart_revenue': chart_revenue,
        'chart_orders': chart_orders,
        'top_products': top_products,
        'top_categories': top_categories,
        'status_counts': status_counts,
        'payment_breakdown': payment_breakdown,
    }
    return render(request, 'admin/accounts/analytics.html', context)



@staff_member_required(login_url='admin_login')
def admin_profile(request):

    return render(request, 'admin/accounts/admin_profile.html')


@staff_member_required(login_url='admin_login')
def admin_edit_profile(request):

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        phone_number = request.POST.get('phone_number').strip()
        
        profile_picture = request.FILES.get('profile_picture')

        request.user.username = username
        request.user.email = email
        
        if hasattr(request.user, 'phone_number'):
            request.user.phone_number = phone_number
            
        if profile_picture and hasattr(request.user, 'profile_image'):
            request.user.profile_image = profile_picture

        request.user.save()

        return redirect('admin_profile')

    return render(request, 'admin/accounts/edit_profile.html')




def admin_logout(request):

    logout(request)

    return redirect('admin_login')