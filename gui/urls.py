from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import register
from .views import register_and_login, DogDetailView, ShelterDetailView, create_post, edit_shelter, EditDogPostView, \
    delete_post


urlpatterns = [
    path('', views.index, name='index'),
    path('login', auth_views.LoginView.as_view(), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('register/', register, name='register'),
    path('register-login/', register_and_login, name='register_and_login'),
    path('dogs/<int:pk>/', DogDetailView.as_view(), name='dog_details'),
    path('shelters/<int:pk>/', ShelterDetailView.as_view(), name='shelter_details'),
    path('create-post/', create_post, name='create_post'),
    path('shelter/edit/<int:pk>/', edit_shelter, name='edit_shelter'),
    path('dogs/edit/<int:pk>/', EditDogPostView.as_view(), name='edit_post'),
    path('delete-post/<int:post_id>/', delete_post, name='delete_post'),
]
