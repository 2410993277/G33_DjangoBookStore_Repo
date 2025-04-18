from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile
from .forms import UserProfileForm, AppUserForm

from django.contrib.auth import get_user_model
User = get_user_model()  # Use your custom us


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')


        if password != cpassword:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        else:
            try:
                validate_password(password)
                User.objects.create_user(
                    email=email,
                    name=name,
                    phone=phone,
                    address=address,
                    gender=gender,
                    password=password
                )
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('login')
            except ValidationError as e:
                for error in e:
                    messages.error(request, error)
    return render(request, 'accounts/register.html')




def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')


        user = authenticate(request, email=email, password=password)
        if user:
            # Determine if the role matches the actual user status
            if (selected_role == 'admin' and user.is_superuser) or (selected_role == 'user' and not user.is_superuser):
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials: Role mismatch")
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html',)





@login_required
def logout_view(request):
    logout(request)
    return redirect('book_list')



@login_required
def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/user_profile.html', {
        'profile': profile,
    })


@login_required
def edit_profile(request):
    user = request.user
    profile = request.user.userprofile

    if request.method == 'POST':
        user_form = AppUserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('view_profile')
    else:
        user_form = AppUserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })