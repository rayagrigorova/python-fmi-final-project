from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView

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
                user_role = reg_form.cleaned_data.get('role')
                registration_code = None
                if user_role == 'shelter':
                    registration_code_input = reg_form.cleaned_data.get('registration_code')
                    try:
                        registration_code = RegistrationCode.objects.get(code=registration_code_input, is_activated=False)
                        registration_code.is_activated = True
                        registration_code.save()
                    except RegistrationCode.DoesNotExist:
                        reg_form.add_error('registration_code', 'Invalid or already activated registration code.')
                        return render(request, 'registration/register_and_login.html', {
                            'reg_form': reg_form,
                            'login_form': login_form
                        })

                user = reg_form.save(commit=False)
                user.set_password(reg_form.cleaned_data['password'])
                user.save()

                return redirect(reverse('login'))

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
    context_object_name = 'shelter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shelter = self.get_object()
        m = folium.Map(location=[shelter.latitude, shelter.longitude], zoom_start=15)
        folium.Marker([shelter.latitude, shelter.longitude], tooltip=shelter.name).add_to(m)
        context['map_html'] = m._repr_html_()
        return context


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


class EditDogPostView(UpdateView):
    model = DogAdoptionPost
    form_class = DogAdoptionPostForm
    template_name = 'edit_dog_post.html'
    success_url = reverse_lazy('index')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(shelter__user=self.request.user)

@login_required(login_url='/register-login')
def delete_post(request, post_id):
    post = get_object_or_404(DogAdoptionPost, id=post_id)

    if request.user != post.shelter.user:
        return redirect('index')

    post.delete()
    return redirect('index')
