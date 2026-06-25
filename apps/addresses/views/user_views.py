from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect

from apps.addresses.models import Address
import re

from django.contrib import messages

@login_required(login_url='login')
def address_list(request):

    addresses = Address.objects.filter(
        user=request.user
    ).order_by(
        '-is_default',
        '-id'
    )

    context = {
        'addresses': addresses
    }

    return render(
        request,
        'user/addresses/address_list.html',
        context
    )


@login_required(login_url='login')
def add_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', '').strip()
        address = request.POST.get('address', '').strip()
        address_type = request.POST.get('address_type', 'HOME')
        is_default = bool(request.POST.get('is_default'))

        context = {
            'full_name': full_name,
            'phone_number': phone_number,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country,
            'address': address,
            'address_type': address_type,
            'is_default': is_default,
        }

        if not full_name:
            messages.error(request, 'Full name is required')
            return render(request, 'user/addresses/add_address.html', context)
        if len(full_name) < 3:
            messages.error(request, 'Full name must be at least 3 letters')
            return render(request, 'user/addresses/add_address.html', context)
        if not re.match(r'^[A-Za-z ]+$', full_name):
            messages.error(request, 'Full name can contain only letters and spaces')
            return render(request, 'user/addresses/add_address.html', context)

        if not re.match(r'^[6-9][0-9]{9}$', phone_number):
            messages.error(request, 'Enter a valid phone number')
            return render(request, 'user/addresses/add_address.html', context)

        if not city:
            messages.error(request, 'City is required')
            return render(request, 'user/addresses/add_address.html', context)
        if not re.match(r'^[A-Za-z ]+$', city):
            messages.error(request, 'Invalid city name')
            return render(request, 'user/addresses/add_address.html', context)

        if not state:
            messages.error(request, 'State is required')
            return render(request, 'user/addresses/add_address.html', context)
        if not re.match(r'^[A-Za-z ]+$', state):
            messages.error(request, 'Invalid state name')
            return render(request, 'user/addresses/add_address.html', context)

        if not re.match(r'^[1-9][0-9]{5}$', postal_code):
            messages.error(request, 'Enter a valid PIN code')
            return render(request, 'user/addresses/add_address.html', context)

        if not address:
            messages.error(request, 'Address is required')
            return render(request, 'user/addresses/add_address.html', context)
        if len(address) < 10:
            messages.error(request, 'Address is too short')
            return render(request, 'user/addresses/add_address.html', context)

        if address_type not in ['HOME', 'WORK', 'OTHER']:
            messages.error(request, 'Invalid address type')
            return render(request, 'user/addresses/add_address.html', context)

        if Address.objects.filter(user=request.user).count() >= 10:
            messages.error(request, 'Maximum 10 addresses allowed')
            return redirect('address_list')

        if not Address.objects.filter(user=request.user).exists():
            is_default = True

        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone_number,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            address=address,
            address_type=address_type,
            is_default=is_default
        )
        messages.success(request,'new address added')

        # Beginner-friendly explicit redirection check
        buy_now_id = request.GET.get('buy_now')
        from_checkout = request.GET.get('from_checkout')

        if buy_now_id:
            return redirect(f'/orders/checkout/?buy_now={buy_now_id}')
        elif from_checkout:
            return redirect('checkout')

        return redirect('address_list')

    return render(request, 'user/addresses/add_address.html')
    

@login_required(login_url='login')
def edit_address(request, id):

    address = Address.objects.get(
        id=id,
        user=request.user
    )

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        phone_number = request.POST.get(
            'phone_number',
            ''
        ).strip()

        city = request.POST.get(
            'city',
            ''
        ).strip()

        state = request.POST.get(
            'state',
            ''
        ).strip()

        postal_code = request.POST.get(
            'postal_code',
            ''
        ).strip()

        country = request.POST.get(
            'country',
            ''
        ).strip()

        address_text = request.POST.get(
            'address',
            ''
        ).strip()

        address_type = request.POST.get(
            'address_type',
            'HOME'
        )

        is_default = bool(
            request.POST.get(
                'is_default'
            )
        )

        address.full_name = full_name
        address.phone_number = phone_number
        address.city = city
        address.state = state
        address.postal_code = postal_code
        address.country = country
        address.address = address_text
        address.address_type = address_type
        address.is_default = is_default

        context = {
            'address': address
        }

        if not full_name:
            messages.error(request, 'Full name is required')
            return render(request, 'user/addresses/edit_address.html', context)
        if len(full_name) < 3:
            messages.error(request, 'Full name must be at least 3 letters')
            return render(request, 'user/addresses/edit_address.html', context)
        if not re.match(r'^[A-Za-z ]+$', full_name):
            messages.error(request, 'Full name can contain only letters and spaces')
            return render(request, 'user/addresses/edit_address.html', context)

        if not re.match(r'^[6-9][0-9]{9}$', phone_number):
            messages.error(request, 'Enter a valid phone number')
            return render(request, 'user/addresses/edit_address.html', context)

        if not city:
            messages.error(request, 'City is required')
            return render(request, 'user/addresses/edit_address.html', context)
        if not re.match(r'^[A-Za-z ]+$', city):
            messages.error(request, 'Invalid city name')
            return render(request, 'user/addresses/edit_address.html', context)

        if not state:
            messages.error(request, 'State is required')
            return render(request, 'user/addresses/edit_address.html', context)
        if not re.match(r'^[A-Za-z ]+$', state):
            messages.error(request, 'Invalid state name')
            return render(request, 'user/addresses/edit_address.html', context)

        if not re.match(r'^[1-9][0-9]{5}$', postal_code):
            messages.error(request, 'Enter a valid PIN code')
            return render(request, 'user/addresses/edit_address.html', context)

        if not address_text:
            messages.error(request, 'Address is required')
            return render(request, 'user/addresses/edit_address.html', context)
        if len(address_text) < 10:
            messages.error(request, 'Address is too short')
            return render(request, 'user/addresses/edit_address.html', context)

        if address_type not in ['HOME', 'WORK', 'OTHER']:
            messages.error(request, 'Invalid address type')
            return render(request, 'user/addresses/edit_address.html', context)

        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)

        address.save()
        return redirect('address_list')

    context = {
        'address': address
    }

    return render(
        request,
        'user/addresses/edit_address.html',
        context
    )



@login_required(login_url='login')
def delete_address(request, id):
    try:
        address = Address.objects.get(
            id=id,
            user=request.user
        )
    except Address.DoesNotExist:
        messages.error(request, "Address not found.")
        return redirect('address_list')

    if request.method == 'POST':
        address.delete()
        
        return redirect('address_list')

    context = {
        'address': address
    }
    return render(
        request,
        'user/addresses/delete_address.html',
        context
    )