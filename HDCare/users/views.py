from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import datetime
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from Doctors.models import *
from Hospitals.models import *
from django.contrib.auth import get_user


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

#Signup
@unauthenticated_user
def signup(request):
    form = RegisterationForm()
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            token = get_random_string(length=40)
            Activation.objects.create(token=token, user=user)
            email_subject = "Activate your account"
            message = f'''
                Thank you for your registration,
                please click this link below to confirm your email.
                http://127.0.0.1:8000/activate/{token}
            '''
            from_email = settings.EMAIL_HOST_USER
            to_list = [request.POST['email'], from_email]
            send_mail(email_subject, message, from_email, to_list, fail_silently=True)

            username = form.cleaned_data.get('username')
            messages.success(request,
                             f'''Congratulations {username}, your account has been created successfully,
                             Please check your email to activate acccount''')
            return redirect('signin')
    else:
        form = RegisterationForm()           
    return render(request, 'register.html', {'form': form})


#login
@unauthenticated_user
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return HttpResponseRedirect(reverse('admin:index'))
            else:
                return redirect('profile')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'login.html')

#home
def home(request):
    return render(request, 'home.html')


def activate_account(request, token):
    activate_user = get_object_or_404(Activation, token=token)
    is_valid = (timezone.now() - activate_user.created_at) < datetime.timedelta(hours=24)
    if is_valid and not activate_user.is_used:
        activate_user.is_used = True
        activate_user.save()
        activate_user.user.is_active = True
        activate_user.user.save()
        messages.success(request, "Congrats, your account has been activated succssefully")
    else:
        messages.error(request, "Sorry, your activation is not valid OR may be used before,Please try again later")
    return redirect("signin")

#profile
@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = EditUser(request.POST,instance=request.user)
        if form.is_valid():
            form.initial = {
                'username':  request.POST.get('userame'),
                'first_name':  request.POST.get('first_name'),
                'last_name':  request.POST.get('last_name'),
                'email': request.POST.get('email'),
                'gender':  request.POST.get('gender'),
                'birthdate': request.POST.get('birthdate'),
                'city':request.POST.get('city'),
                'phone':  request.POST.get('phone'),
            }
            form.save()
            messages.success(request, "Your data updated successfully")
            return redirect('profile')
    else:    
        form = EditUser(initial={
            'username': user.username,
            'first_name': user.first_name.capitalize(),
            'last_name': user.last_name.capitalize(),
            'email': user.email,
            'gender': user.gender,
            'birthdate': user.birthdate,
            'city': user.city,
            'phone': user.phone,

            })
    return render(request,'personalPage.html', {'form': form})


@login_required
def password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change-password.html', {'form': form})



@login_required
def appointments(request):
    user = get_user(request)
    doctor_book = UserBook.objects.filter(user=user)
    hospital_book = User_Book.objects.filter(user=user)

    context = {'doctor_book': doctor_book, 'hospital_book': hospital_book}

    return render(request, "appointments.html", context)


#logout
def user_logout(request):
    logout(request)
    return redirect('home')


