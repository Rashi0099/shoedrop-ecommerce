from django.shortcuts import render, redirect

from django.contrib import messages

from django.contrib.auth import authenticate

from django.contrib.auth import login

from django.views.decorators.cache import never_cache

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import logout

from django.contrib.auth import update_session_auth_hash
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



@staff_member_required(
    login_url='admin_login'
)
def admin_dashboard(request):

    return render(
        request,
        'admin/accounts/dashboard.html'
    )

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