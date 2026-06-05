import re

from django.shortcuts import render,redirect

from django.contrib import messages

from django.contrib.auth import get_user_model

from django.views.decorators.cache import never_cache

from django.core.validators import validate_email

from django.core.exceptions import ValidationError

from django.contrib.auth import authenticate

from django.contrib.auth import login

from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail

import random

from datetime import datetime

from django.conf import settings




User=get_user_model()

def landing_page(request):

    return render(
        request,'user/accounts/landing_page.html')
def signup(request):
    print("SIGNUP VIEW HIT")

    if request.user.is_authenticated:

        return redirect('profile')
    
    context={}

    if request.method =='POST':
        
        username=request.POST.get('username').strip()

        email=request.POST.get('email').strip()


        password=request.POST.get('password')

        confirm_password=request.POST.get('confirm_password')

        context={
            'username':username,
            'email':email,
        }
        if not username:
            messages.error(request,'User name is required')
            return render(request,'user/accounts/signup.html',context)

        if len(username)<3:
            messages.error(request,'username must contain al least 3 characters')
            return render(request,'user/accounts/signup.html',context)
        
        if username.isdigit():

            messages.error(request,'username connot contain only numbers')
            return render(request,'user/accounts/signup.html',context)
        
        if not re.match(r'^[A-Za-z0-9_]+$',username):
            messages.error(request,'User name can contain only letters,numbers and underscore')
            return render(request,'user/accounts/signup.html',context)
        
        if User.objects.filter(username=username).exists():
            messages.error(request,'user name alrdy exists')
            return render(request,'user/accounts/signup.html',context)
        
        if not email:
            messages.error(request,'Email is required')
            return render(request,'user/accounts/signup.html',context)

        try:
            validate_email(email)

        except ValidationError:
            messages.error(request,'Enter valid email address')
            return render(request,'user/accounts/signup.html',context)

        if User.objects.filter(email=email).exists():
            messages.error(request,'Email alrdy exists')
            return render(request,'user/accounts/signup.html',context)
        
        
        if not password or not confirm_password:
            messages.error(request,'password field cannot be empty')
            return render(request,'user/accounts/signup.html',context)
        
        if len(password)<8:
            messages.error(request,'password must contain 8 characters')
            return render(request,'user/accounts/signup.html',context)
        
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).+$',password):
            messages.error(request,'Password must contain uppercase, lowercase and numbers')
            return render(request,'user/accounts/signup.html',context)
        
        if password != confirm_password:
            messages.error(request,'password do not match ')
            return render(request,'user/accounts/signup.html',context)
        
        otp = str(random.randint(1000,9999))

        request.session['otp'] = otp
        

        request.session['username'] = username

        request.session['email'] = email

        request.session['password'] = password

        request.session['otp_created_at'] = datetime.now().timestamp()
        
            

        send_mail(
            'Shoedrop OTP Verification',
            f'Your OTP is {otp}',
            None,
            [email],
            fail_silently=False
        )

        return redirect('verify_otp')
                
    return render(request,'user/accounts/signup.html',context)


def verify_otp(request):
    if not request.session.get('email'):
        return redirect('signup')

    if request.method == 'POST':

        entered_otp = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '')
        )

        session_otp = request.session.get('otp')
        otp_created_at = request.session.get(
            'otp_created_at'
        )
        if not otp_created_at:
            messages.error(request, 'OTP expired. Please sign up again.')
            for key in ['otp', 'username', 'email', 'password', 'otp_created_at']:
                request.session.pop(key, None)
            return redirect('signup')

        current_time = datetime.now().timestamp()

        # ✅ Fix — clear the expired OTP so user sees clean resend state:
        if current_time - otp_created_at > 60:
            messages.error(request, 'OTP expired. Please resend OTP.')
            request.session.pop('otp', None)
            request.session.pop('otp_created_at', None)
            return redirect('verify_otp')



        if entered_otp == session_otp:

            User.objects.create_user(
                username=request.session.get('username'),
                email=request.session.get('email'),
                password=request.session.get('password')
            )

            request.session.pop('otp', None)
            request.session.pop('username', None)
            request.session.pop('email', None)
            request.session.pop('password', None)
            request.session.pop('otp_created_at',None)

            messages.success(
                request,
                'Account created successfully'
            )

            return redirect('login')
        messages.error(
        request,
        'Invalid OTP'
        )

    otp_created_at = request.session.get(
        'otp_created_at'
    )

    remaining_time = 60

    if otp_created_at:

        remaining_time = max(
            0,
            60 - int(
                datetime.now().timestamp() - otp_created_at
            )
        )

    return render(
        request,
        'user/accounts/verify_otp.html',
        {
            'remaining_time':remaining_time
        }
    )
        
def resend_otp(request):

    email = request.session.get('email')

    if not email:
        return redirect('signup')

    otp_created_at = request.session.get('otp_created_at')
    if otp_created_at and (datetime.now().timestamp() - otp_created_at) < 30:
        messages.error(request, 'Please wait 30 seconds before requesting a new OTP.')
        return redirect('verify_otp')

    
    otp = str(random.randint(1000,9999))

    request.session['otp'] = otp

    request.session['otp_created_at'] = datetime.now().timestamp()


    send_mail(
        'Shoedrop OTP Verification',
        f'Your OTP is {otp}',
        None,
        [email],
        fail_silently=False
    )

    messages.success(
        request,
        'New OTP sent successfully'
    )

    return redirect('verify_otp')
@never_cache
def login_view(request):

    if request.user.is_authenticated:
        return redirect('landing_page')

    if request.method == 'POST':

        email = request.POST.get('email').strip()

        password = request.POST.get('password')

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(request,'Login successful')
            return redirect('landing_page')

        messages.error(request,'Invalid email or password')

    return render(request,'user/accounts/login.html')


def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get(
            'email',
            ''
        ).strip()

        if not User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                'Email not found'
            )

            return render(
                request,
                'user/accounts/forgot_password.html'
            )

        otp = str(
            random.randint(1000,9999)
        )

        request.session[
            'reset_email'
        ] = email

        request.session[
            'reset_otp'
        ] = otp

        request.session[
            'reset_otp_created_at'
        ] = datetime.now().timestamp()

        send_mail(
            'Shoedrop Password Reset OTP',
            f'Your OTP is {otp}',
            None,
            [email],
            fail_silently=False
        )

        return redirect(
            'forgot_password_verify_otp'
        )

    return render(
        request,
        'user/accounts/forgot_password.html'
    )
def forgot_password_verify_otp(request):
    

    if request.method == 'POST':

        entered_otp = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '')
        )

        session_otp = request.session.get('reset_otp')
        otp_created_at = request.session.get('reset_otp_created_at')

        if not otp_created_at or (datetime.now().timestamp() - otp_created_at) > 60:
            messages.error(request, 'OTP expired. Please request a new one.')
            return redirect('forgot_password')

        if entered_otp == session_otp:
            request.session['otp_verified'] = True
            return redirect('reset_password')

        messages.error(request, 'Invalid OTP')

    return render(
        request,
        'user/accounts/forgot_password_verify_otp.html'
    )
def resend_reset_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    otp_created_at = request.session.get('reset_otp_created_at')
    if otp_created_at and (datetime.now().timestamp() - otp_created_at) < 30:
        messages.error(request, 'Please wait 30 seconds before requesting a new OTP.')
        return redirect('forgot_password_verify_otp')
    import secrets
    otp = str(secrets.randbelow(900000) + 100000)
    request.session['reset_otp'] = otp
    request.session['reset_otp_created_at'] = datetime.now().timestamp()
    send_mail(
        'Shoedrop Password Reset OTP',
        f'Your OTP is {otp}',
        None,
        [email],
        fail_silently=False
    )
    messages.success(request, 'New OTP sent successfully.')
    return redirect('forgot_password_verify_otp')

def reset_password(request):

    if not request.session.get('reset_email') or not request.session.get('otp_verified'):
        return redirect('forgot_password')


    if request.method == 'POST':

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match'
            )

            return render(
                request,
                'user/accounts/reset_password.html'
            )

        user = User.objects.get(
            email=request.session.get(
                'reset_email'
            )
        )

        user.set_password(
            password
        )

        user.save()

        request.session.pop('reset_email', None)
        request.session.pop('reset_otp', None)
        request.session.pop('reset_otp_created_at', None)
        request.session.pop('otp_verified', None)


        messages.success(
            request,
            'Password reset successful'
        )

        return redirect(
            'login'
        )

    return render(
        request,
        'user/accounts/reset_password.html'
    )


@never_cache
@login_required(login_url='login')
def profile(request):

    return render(
        request,
        'user/accounts/userprofile.html'
    )

@login_required(login_url='login')
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST.get(
            'current_password'
        )

        new_password = request.POST.get(
            'new_password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if not request.user.check_password(
            current_password
        ):
            

            messages.error(
                request,
                'Current password is incorrect'
            )

            return redirect(
                'change_password'
            )

        if new_password != confirm_password:

            messages.error(
                request,
                'Passwords do not match'
            )

            return redirect(
                'change_password'
            )

        request.user.set_password(
            new_password
        )

        request.user.save()

        messages.success(
            request,
            'Password changed successfully'
        )

        return redirect(
            'login'
        )

    return render(
        request,
        'user/accounts/change_password.html'
    )


@login_required(login_url='login')
def edit_profile(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        ).strip()

        phone_number = request.POST.get(
            'phone_number'
        ).strip()


        profile_image = request.FILES.get(
            'profile_image'
        )
        email=request.POST.get(
            'email',
        ).strip()
        remove_photo=request.POST.get(
            'remove_photo'
        )
        old_email = request.user.email

        if remove_photo == '1':

            if request.user.profile_image:

                request.user.profile_image.delete(
                    save=False
                )

                request.user.profile_image = None       

        if User.objects.exclude(
            id=request.user.id
        ).filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists'
            )
            return redirect('edit_profile')
        
        if not username:
            messages.error(
                request,
                'Username is required'
            )
            return redirect('edit_profile')

        if not re.match(
            r'^[A-Za-z0-9_]+$',
            username
        ):
            messages.error(
                request,
                'Username can contain only letters, numbers and underscore'
            )
            return redirect('edit_profile')
        if phone_number:

            if not re.match(
                r'^[0-9]{10}$',
                phone_number
            ):
                messages.error(
                    request,
                    'Enter a valid 10 digit phone number'
                )
                return redirect('edit_profile')
        allowed_types = [
    'image/jpeg',
    'image/png',
    'image/webp'
]

        if profile_image:

            if profile_image.content_type not in allowed_types:

                messages.error(
                    request,
                    'Only JPG, PNG and WEBP allowed'
                )
                return redirect('edit_profile')
                
            if profile_image.size > 2 * 1024 * 1024:

                messages.error(
                    request,
                    'Image must be less than 2MB'
                )

                return redirect(
                    'edit_profile'
                )


           

        request.user.username = username
        request.user.phone_number = phone_number

        if profile_image:

            if request.user.profile_image:
                request.user.profile_image.delete(
                    save=False
                )

            request.user.profile_image = profile_image
        try:
            validate_email(email)

        except ValidationError:

            messages.error(
                request,
                'Enter a valid email address'
            )

            return redirect(
                'edit_profile'
            )

        request.user.save()
        
        if email != old_email:

            if User.objects.exclude(
                id=request.user.id
            ).filter(
                email=email
            ).exists():

                messages.error(
                    request,
                    'Email already exists'
                )

                return redirect(
                    'edit_profile'
                )

            otp = str(
                random.randint(
                    1000,
                    9999
                )
            )

            request.session['new_email'] = email
            request.session['email_otp'] = otp
            request.session['email_otp_created_at'] = datetime.now().timestamp()

            send_mail(
                'Email Verification OTP',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            messages.success(
            request,
            'OTP sent to your new email address'
        )

            return redirect(
                'verify_email_otp'
            )

        messages.success(
            request,
            'Profile updated successfully'
        )

        return redirect(
            'profile'
)
       

    return render(
        request,
        'user/accounts/edit_profile.html'
    )
@login_required(login_url='login')
def verify_email_otp(request):

    if request.method == 'POST':

        entered_otp = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '')
        )
        otp_created_at = request.session.get(
    'email_otp_created_at'
        )

        if not otp_created_at:

            messages.error(
                request,
                'OTP expired'
            )

            return redirect(
                'edit_profile'
            )

        if (
            datetime.now().timestamp()
            - otp_created_at
        ) > 60:

            messages.error(
                request,
                'OTP expired'
            )

            return redirect(
                'edit_profile'
            )

        if entered_otp == request.session.get(
            'email_otp'
        ):

            request.user.email = request.session.get(
                'new_email'
            )

            request.user.save()

            request.session.pop(
                'new_email',
                None
            )

            request.session.pop(
                'email_otp',
                None
            )
            request.session.pop('email_otp_created_at',
                None
            )

            messages.success(
                request,
                'Email updated successfully'
            )

            return redirect(
                'profile'
            )

        messages.error(
            request,
            'Invalid OTP'
        )

    return render(
        request,
        'user/accounts/verify_email_otp.html'
    )
@login_required(login_url='login')
def resend_email_otp(request):
    email = request.session.get('new_email')
    if not email:
        return redirect('edit_profile')
    otp_created_at = request.session.get('email_otp_created_at')
    if otp_created_at and (datetime.now().timestamp() - otp_created_at) < 30:
        messages.error(request, 'Please wait 30 seconds before requesting a new OTP.')
        return redirect('verify_email_otp')
    import secrets
    otp = str(secrets.randbelow(900000) + 100000)
    request.session['email_otp'] = otp
    request.session['email_otp_created_at'] = datetime.now().timestamp()
    send_mail(
        'Email Verification OTP',
        f'Your OTP is {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )
    messages.success(request, 'New OTP sent to your email.')
    return redirect('verify_email_otp')

def logout_view(request):

    logout(request)

    return redirect('landing_page')