from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

import razorpay
from django.conf import settings

from apps.orders.views.user_views import create_order, calculate_order_amount

#5267 3181 8797 5449
@login_required(login_url='login')
def cod_payment(request):

    order = create_order(
        request,
        payment_method='COD',
        payment_status='pending'
    )

    if not order:
        messages.error(request, 'Unable to place order.')
        return redirect('checkout')

    return redirect(f'/orders/order-success/?order_id={order.id}')


@login_required(login_url='login')
def razorpay_payment(request):

    address_id = request.POST.get('address_id')
    buy_now_id = request.POST.get('buy_now')

    if not address_id:
        messages.error(request, 'Please select an address.')
        return redirect('checkout')

    totals = calculate_order_amount(request, buy_now_id)

    if not totals:
        messages.error(request, 'Unable to process payment. Check your cart.')
        return redirect('checkout')

    request.session['address_id'] = address_id
    request.session['buy_now_id'] = buy_now_id or ''

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        'amount': totals['amount_paise'],
        'currency': 'INR',
        'payment_capture': 1
    })

    context = {
        'razorpay_order_id': payment['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': totals['amount_paise'],
        'grand_total': totals['grand_total']
    }

    return render(request, 'user/payments/razorpay_payment.html', context)


@csrf_exempt
@login_required(login_url='login')
def verify_razorpay_payment(request):

    if request.method != 'POST':
        return redirect('checkout')

    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })

    except razorpay.errors.SignatureVerificationError:
        request.session.pop('address_id', None)
        request.session.pop('buy_now_id', None)
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('checkout')

    mutable_post = request.POST.copy()
    mutable_post['address_id'] = request.session.get('address_id')

    buy_now_session = request.session.get('buy_now_id', '')
    mutable_post['buy_now'] = buy_now_session if buy_now_session else None

    request.POST = mutable_post

    order = create_order(request, payment_method='Razorpay', payment_status='paid')

    request.session.pop('address_id', None)
    request.session.pop('buy_now_id', None)

    if not order:
        messages.error(request, 'Payment received but order failed. Contact support. Payment ID: ' + (razorpay_payment_id or ''))
        return redirect('checkout')

    return redirect(f'/orders/order-success/?order_id={order.id}')


@login_required(login_url='login')
def wallet_payment(request):

    address_id = request.POST.get('address_id')
    buy_now_id = request.POST.get('buy_now')

    if not address_id:
        messages.error(request, 'Please select an address.')
        return redirect('checkout')

    totals = calculate_order_amount(request, buy_now_id)

    if not totals:
        messages.error(request, 'Unable to process payment. Check your cart.')
        return redirect('checkout')

    grand_total = totals['grand_total']

    # Get or create the wallet for the user
    from apps.payments.models import Wallet, WalletTransaction
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    if wallet.balance < grand_total:
        messages.error(request, 'Insufficient wallet balance.')
        return redirect('checkout')

    order = create_order(request, payment_method='Wallet', payment_status='paid')

    if not order:
        messages.error(request, 'Unable to place order.')
        return redirect('checkout')

    wallet.balance -= grand_total
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=grand_total,
        transaction_type='debit',
        description=f'Order #{order.id} payment'
    )

    return redirect(f'/orders/order-success/?order_id={order.id}')
