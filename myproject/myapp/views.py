from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
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
                    # Session expires when the user closes their browser
                    request.session.set_expiry(0)
                else:
                    # Session lasts 2 weeks (1209600 seconds)
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


def logout_view(request):
    """
    Logs out the user and redirects to the login screen with an informative message.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def home_view(request):
    """
    Protected home/dashboard view to demonstrate successful authentication.
    """
    return render(request, 'myapp/home.html', {'user': request.user})
