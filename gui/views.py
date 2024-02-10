from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.views.generic import DetailView

from .forms import UserRegistrationForm
from django.shortcuts import render, redirect
from .models import RegistrationCode, Shelter, DogAdoptionPost

import folium


@login_required(login_url='/register-login')
def index(request):
    dogs = DogAdoptionPost.objects.all()
    shelters = Shelter.objects.all()
    return render(request, 'index.html', {'dogs': dogs, 'shelters': shelters})


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
                pass

            if reg_form.is_valid() and valid_code:
                user = reg_form.save(commit=False)
                user.set_password(reg_form.cleaned_data['password'])
                user.save()
                code_entry.is_activated = True
                code_entry.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect(reverse('login'))
        elif 'action' in request.POST and request.POST['action'] == 'login':
            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['username'],
                                    password=login_form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect(reverse('index'))

    return render(request, 'registration/register_and_login.html', {'reg_form': reg_form, 'login_form': login_form})


class DogDetailView(DetailView):
    model = DogAdoptionPost
    template_name = 'dog_details.html'

class ShelterDetailView(DetailView):
    model = Shelter
    template_name = 'shelter_details.html'


def shelter_map_view(request, shelter_id):
    shelter = Shelter.objects.get(pk=shelter_id)
    m = folium.Map(location=[shelter.latitude, shelter.longitude], zoom_start=15)
    folium.Marker([shelter.latitude, shelter.longitude], tooltip=shelter.name).add_to(m)
    map_html = m._repr_html_()
    context = {'map_html': map_html}
    return render(request, 'shelter_map.html', context)
