from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect


@login_required(login_url='/register-login')
def index(request):
    """Welcome page."""
    return render(request, 'index.html')


from .models import RegistrationCode


def register_and_login(request):
    # Initialize forms regardless of request method or action
    reg_form = UserRegistrationForm(request.POST or None)
    login_form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'register':
            # Additional validation for registration code
            registration_code = request.POST.get('registration_code')
            username = request.POST.get('username')
            valid_code = False

            try:
                code_entry = RegistrationCode.objects.get(username=username, code=registration_code, is_activated=False)
                valid_code = True
            except RegistrationCode.DoesNotExist:
                messages.error(request, "Invalid registration code for this username or code already activated.")

            if reg_form.is_valid() and valid_code:
                user = reg_form.save(commit=False)
                user.set_password(reg_form.cleaned_data['password'])
                user.save()
                code_entry.is_activated = True
                code_entry.save()
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