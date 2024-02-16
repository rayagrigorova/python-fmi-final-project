from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView

from .forms import UserRegistrationForm, DogAdoptionPostForm, ShelterForm, SortFilterForm, CommentForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import RegistrationCode, Shelter, DogAdoptionPost, Comment, PostSubscription, Notification

import folium
from django.contrib import messages


@login_required(login_url='/register-login')
def index(request):
    shelters = Shelter.objects.all()
    dogs = DogAdoptionPost.objects.filter(adoption_stage__in=['active', 'in_process'])

    for dog in dogs:
        dog.user_is_subscribed = PostSubscription.objects.filter(user=request.user, post=dog).exists()

    form = SortFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['shelter']:
            dogs = dogs.filter(shelter=form.cleaned_data['shelter'])
        if form.cleaned_data['size']:
            dogs = dogs.filter(size=form.cleaned_data['size'])
        if form.cleaned_data['breed']:
            dogs = dogs.filter(breed__icontains=form.cleaned_data['breed'])
        if form.cleaned_data['gender']:
            dogs = dogs.filter(gender=form.cleaned_data['gender'])
        if form.cleaned_data['sort_by']:
            # If the sort criteria is size, then use a
            # custom sorting function that assigns each size a number
            if form.cleaned_data['sort_by'] == 'size':
                # Convert QuerySet to a list
                dogs = list(dogs)
                size_order = {'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5}
                dogs.sort(key=lambda x: size_order.get(x.size, 0))
            else:
                dogs = dogs.order_by(form.cleaned_data['sort_by'])

    return render(request, 'index.html', {'dogs': dogs, 'shelters': shelters, 'form': form})


def register_and_login(request):
    reg_form = UserRegistrationForm()
    login_form = AuthenticationForm()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'register':
            # Create UserRegistrationForm instance with POST data from the request.
            # The form is populated with the data submitted by the user.
            reg_form = UserRegistrationForm(request.POST)
            if reg_form.is_valid():
                user_role = reg_form.cleaned_data.get('role')
                if user_role == 'shelter':
                    registration_code_input = reg_form.cleaned_data.get('registration_code')
                    try:
                        registration_code = RegistrationCode.objects.get(code=registration_code_input,
                                                                         is_activated=False)
                        registration_code.is_activated = True
                        registration_code.save()
                    except RegistrationCode.DoesNotExist:
                        # If the needed code doesn't exist, render the register_and_login form again
                        return render(request, 'registration/register_and_login.html', {
                            'reg_form': reg_form,
                            'login_form': login_form
                        })

                # Create a new instance of the model associated with the form (in this case, CustomUser)
                # commit=False means 'don't save to the database yet'
                user = reg_form.save(commit=False)
                user.set_password(reg_form.cleaned_data['password'])
                # Save the modified user instance to the database
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


# Django's DetailView is used to display a details page for an object from the database
class DogDetailView(DetailView):
    model = DogAdoptionPost
    template_name = 'dog_details.html'
    context_object_name = 'dog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.object)
        context['comment_form'] = CommentForm()
        context['dog_post'] = self.object
        return context


class ShelterDetailView(DetailView):
    model = Shelter
    template_name = 'shelter_details.html'
    context_object_name = 'shelter'

    # get_context_data is used to pass additional data to the template
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
        messages.error(request, "You do not have permission to create a post.")
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
    #  Try to find a Shelter object that matches the provided primary key
    #  and belongs to the currently logged-in user
    shelter = get_object_or_404(Shelter, pk=pk, user=request.user)
    if request.method == 'POST':
        # A ShelterForm instance is created and populated
        # with data from the request and the shelter instance to be edited
        form = ShelterForm(request.POST, instance=shelter)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        # A GET request: (the form is being accessed for the first time)
        # populate it with the shelter's existing details
        form = ShelterForm(instance=shelter)
    return render(request, 'edit_shelter.html', {'form': form})


class EditDogPostView(UpdateView):
    model = DogAdoptionPost  # specify the model to be updated
    form_class = DogAdoptionPostForm
    template_name = 'edit_dog_post.html'
    # specify the URL to redirect; reverse_lazy() is used so that
    # the URL is not loaded before the app is ready
    success_url = reverse_lazy('index')

    def get_queryset(self):
        """
        Customize the queryset to ensure users can
        only edit their own posts by filtering DogAdoptionPost objects.
        """
        qs = super().get_queryset()
        # 'shelter' is the FK for the post, '__' navigates through model fields' relationships
        # 'user' is a field in the Shelter model
        return qs.filter(shelter__user=self.request.user)


@login_required(login_url='/register-login')
def delete_post(request, post_id):
    post = get_object_or_404(DogAdoptionPost, id=post_id)

    if request.user != post.shelter.user:
        return redirect('index')

    post.delete()
    return redirect('index')


@login_required(login_url='/register-login')
def archive_page(request):
    archived_dogs = DogAdoptionPost.objects.filter(adoption_stage='completed')
    return render(request, 'archive_page.html', {'archived_dogs': archived_dogs})


# 'pk' is used to identify the post the comment is associated with
def create_comment(request, pk):
    dog_post = get_object_or_404(DogAdoptionPost, pk=pk)
    if request.method == "POST":
        # Create an instance of the form and populate it with the data from the request
        form = CommentForm(request.POST)
        if form.is_valid():
            # Save form data to comment , but don't commit yet
            comment = form.save(commit=False)
            comment.post = dog_post
            comment.author = request.user
            comment.save()
    return redirect('dog_details', pk=dog_post.pk)


@login_required(login_url='/register-login')
def edit_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk, author=request.user, post_id=post_pk)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('dog_details', pk=post_pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form})


@login_required(login_url='/register-login')
def delete_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk, author=request.user, post_id=post_pk)
    comment.delete()
    return redirect('dog_details', pk=post_pk)


@login_required(login_url='/register-login')
def subscribe_to_post(request, post_id):
    post = get_object_or_404(DogAdoptionPost, id=post_id)
    if request.user == post.shelter.user:
        return redirect('index')

    try:
        PostSubscription.objects.get(user=request.user)
    except PostSubscription.DoesNotExist:
        PostSubscription.objects.create(user=request.user, post=post)
    return redirect('index')


@login_required(login_url='/register-login')
def unsubscribe_from_post(request, post_id):
    post = get_object_or_404(DogAdoptionPost, id=post_id)
    if request.user == post.shelter.user:
        return redirect('index')

    subscription_to_remove = PostSubscription.objects.filter(user=request.user, post=post)
    subscription_to_remove.delete()
    return redirect('index')


@login_required(login_url='/register-login')
def user_notifications(request):
    notifications = request.user.notifications.all()
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required(login_url='/register-login')
def mark_notifications_read(request):
    """Mark all messages as 'read' after the user leaves the notifications page"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return HttpResponse('OK', status=200)