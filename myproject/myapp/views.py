from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_view(request):
    """
    Renders the login UI and handles authentication.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'myapp/login.html', {'username': username})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if not remember_me:
                    # Session expires when user closes the browser
                    request.session.set_expiry(0)
                else:
                    # Session lasts 14 days (1209600 seconds)
                    request.session.set_expiry(1209600)

                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Your account has been deactivated. Please contact support.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

        return render(request, 'myapp/login.html', {'username': username})

    next_url = request.GET.get('next', '')
    return render(request, 'myapp/login.html', {'next': next_url})


def signup_view(request):
    """
    Renders registration UI and creates new user accounts.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Basic validations
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'myapp/signup.html', {'username': username, 'email': email})

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'myapp/signup.html', {'username': username, 'email': email})

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'myapp/signup.html', {'username': username, 'email': email})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'A user with that username already exists.')
            return render(request, 'myapp/signup.html', {'username': username, 'email': email})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return render(request, 'myapp/signup.html', {'username': username, 'email': email})

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f'Account created successfully! Welcome to FutureByte, {user.username}.')
        return redirect('home')

    return render(request, 'myapp/signup.html')


def forgot_password_view(request):
    """
    Renders forgot password / password reset request UI.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your registered email address.')
            return render(request, 'myapp/forgot_password.html')

        # Generic safe feedback to prevent account enumeration
        messages.success(
            request,
            f'If an account associated with {email} exists, password reset instructions have been sent.'
        )
        return render(request, 'myapp/forgot_password.html', {'submitted': True})

    return render(request, 'myapp/forgot_password.html')


def logout_view(request):
    """
    Logs out user and redirects to login.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def home_view(request):
    """
    Protected dashboard/home view.
    """
    return render(request, 'myapp/home.html', {'user': request.user})
