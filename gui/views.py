from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect


@login_required(login_url='/register-login')
def index(request):
    """Welcome page."""
    return render(request, 'index.html')


def register_and_login(request):
    # Initialize forms regardless of request method or action
    reg_form = UserRegistrationForm(request.POST or None)
    login_form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'register':
            if reg_form.is_valid():
                user = reg_form.save(commit=False)
                user.set_password(reg_form.cleaned_data['password'])
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('login')
        elif 'action' in request.POST and request.POST['action'] == 'login':
            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['username'],
                                    password=login_form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect('index')

    return render(request, 'registration/register_and_login.html', {'reg_form': reg_form, 'login_form': login_form})
