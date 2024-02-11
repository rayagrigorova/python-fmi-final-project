from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.views.generic import DetailView

from .forms import UserRegistrationForm, DogAdoptionPostForm, ShelterForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import RegistrationCode, Shelter, DogAdoptionPost

import folium


@login_required(login_url='/register-login')
def index(request):
    dogs = DogAdoptionPost.objects.all()
    shelters = Shelter.objects.all()
    return render(request, 'index.html', {'dogs': dogs, 'shelters': shelters})


def register_and_login(request):
    reg_form = UserRegistrationForm()
    login_form = AuthenticationForm()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'register':
            reg_form = UserRegistrationForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save(commit=False)
                user.set_password(reg_form.cleaned_data['password'])
                user.save()
                return redirect(reverse('login'))  #
        elif action == 'login':
            login_form = AuthenticationForm(data=request.POST, request=request)
            if login_form.is_valid():
                user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                if user is not None:
                    login(request, user)
                    return redirect(reverse('index'))

    return render(request, 'registration/register_and_login.html', {
        'reg_form': reg_form,
        'login_form': login_form
    })


class DogDetailView(DetailView):
    model = DogAdoptionPost
    template_name = 'dog_details.html'
    context_object_name = 'dog'


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


@login_required(login_url='/register-login')
def create_post(request):
    if request.user.role != 'shelter':
        return redirect('index')

    if request.method == 'POST':
        form = DogAdoptionPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.shelter = request.user.shelter
            post.save()
            return redirect('index')
    else:
        form = DogAdoptionPostForm()

    return render(request, 'create_post.html', {'form': form})


@login_required(login_url='/register-login')
def edit_shelter(request, pk):
    shelter = get_object_or_404(Shelter, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ShelterForm(request.POST, instance=shelter)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the index page or wherever appropriate
    else:
        form = ShelterForm(instance=shelter)
    return render(request, 'edit_shelter.html', {'form': form})
