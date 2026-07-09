from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.coupons.models import Coupon
from apps.orders.views.user_views import calculate_order_amount

@login_required(login_url='login')
def apply_coupon(request):
    referer = request.META.get('HTTP_REFERER', '/orders/checkout/')
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        
        if not coupon_code:
            messages.error(request, 'Please enter a coupon code.')
            return HttpResponseRedirect(referer)

        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid or expired coupon code.')
            return HttpResponseRedirect(referer)

        if not coupon.is_valid():
            messages.error(request, 'This coupon is no longer valid.')
            return HttpResponseRedirect(referer)

        buy_now_id = request.POST.get('buy_now') or request.GET.get('buy_now')
        totals = calculate_order_amount(request, buy_now_id)

        if not totals:
            messages.error(request, 'Your cart is empty or items are unavailable.')
            return HttpResponseRedirect(referer)
        
        subtotal = totals['subtotal']
        if subtotal < coupon.min_cart_value:
            messages.error(request, f'This coupon requires a minimum cart value of ₹{coupon.min_cart_value}.')
            return HttpResponseRedirect(referer)
        
        # Save to session
        request.session['applied_coupon'] = coupon.coupon_code
        messages.success(request, f'Coupon "{coupon.coupon_name}" applied successfully!')
        
    return HttpResponseRedirect(referer)

@login_required(login_url='login')
def remove_coupon(request):
    referer = request.META.get('HTTP_REFERER', '/orders/checkout/')
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        messages.success(request, 'Coupon removed successfully.')
    return HttpResponseRedirect(referer)
