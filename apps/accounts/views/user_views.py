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
        

        user=User.objects.create_user(username=username,email=email,password=password)
        user.save()
        messages.success(request,'Account created successfully')
        return redirect('login')
    return render(request,'user/accounts/signup.html',context)


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
            return redirect('profile')

        messages.error(request,'Invalid email or password')

    return render(request,'user/accounts/login.html')
@never_cache
@login_required(login_url='login')
def profile(request):

    return render(
        request,
        'user/accounts/userprofile.html'
    )
def logout_view(request):

    logout(request)

    return redirect('landing_page')