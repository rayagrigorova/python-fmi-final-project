from django.contrib.auth import get_user_model
from django import forms
from django.shortcuts import render, redirect
from .models import RegistrationCode


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'role', 'registration_code']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        registration_code = cleaned_data.get('registration_code')
        username = cleaned_data.get('username')

        if role == 'shelter':
            if registration_code:
                try:
                    code_obj = RegistrationCode.objects.get(code=registration_code, username=username,
                                                            is_activated=False)
                except RegistrationCode.DoesNotExist:
                    self.add_error('registration_code',
                                   "Invalid registration code for this username or code already activated.")
            else:
                self.add_error('registration_code', "This field is required for shelters.")

        return cleaned_data


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
