from django.contrib.auth import get_user_model
from django import forms
from django.shortcuts import render, redirect


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'role', 'registration_code']

    def clean_registration_code(self):
        role = self.cleaned_data.get('role')
        registration_code = self.cleaned_data.get('registration_code')
        if role == 'shelter' and registration_code != 'code':
            raise forms.ValidationError("Invalid registration code for shelter.")
        return registration_code


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
