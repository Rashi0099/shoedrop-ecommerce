from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.offers.models import Offer
from apps.products.models import Product


@login_required(login_url='admin_login')
def offer_list(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    offers = Offer.objects.all().order_by('-created_at')

    if search:
        offers = offers.filter(offer_title__icontains=search)

    if status == 'active':
        offers = offers.filter(is_active=True)
    elif status == 'inactive':
        offers = offers.filter(is_active=False)

    context = {
        'offers': offers,
        'search': search,
        'status_filter': status,
    }
    return render(request, 'admin/offers/offer_list.html', context)


@login_required(login_url='admin_login')
def add_offer(request):
    if request.method == 'POST':
        offer_title = request.POST.get('offer_title')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        product_ids = request.POST.getlist('products')

        offer = Offer.objects.create(
            offer_title=offer_title,
            discount_percentage=discount_percentage,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            is_active=True
        )

        if product_ids:
            offer.products.set(Product.objects.filter(id__in=product_ids))

        messages.success(request, 'Offer created successfully.')
        return redirect('offer_list')

    products = Product.objects.all()
    return render(request, 'admin/offers/add_offer.html', {'products': products})


@login_required(login_url='admin_login')
def edit_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    if request.method == 'POST':
        offer.offer_title = request.POST.get('offer_title')
        offer.discount_percentage = request.POST.get('discount_percentage')

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        offer.start_date = start_date if start_date else None
        offer.end_date = end_date if end_date else None
        offer.is_active = request.POST.get('is_active') == 'on'
        offer.save()

        product_ids = request.POST.getlist('products')
        if product_ids:
            offer.products.set(Product.objects.filter(id__in=product_ids))
        else:
            offer.products.clear()

        messages.success(request, 'Offer updated successfully.')
        return redirect('offer_list')

    products = Product.objects.all()
    context = {
        'offer': offer,
        'products': products,
        'start_date_str': offer.start_date.strftime('%Y-%m-%dT%H:%M') if offer.start_date else '',
        'end_date_str': offer.end_date.strftime('%Y-%m-%dT%H:%M') if offer.end_date else '',
    }
    return render(request, 'admin/offers/edit_offer.html', context)


@login_required(login_url='admin_login')
def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.delete()
    messages.success(request, 'Offer deleted successfully.')
    return redirect('offer_list')
