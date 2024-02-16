from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import register_and_login, DogDetailView, ShelterDetailView, create_post, edit_shelter, EditDogPostView, \
    delete_post, archive_page, create_comment

urlpatterns = [
    path('', views.index, name='index'),
    path('login', auth_views.LoginView.as_view(), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('register-login/', register_and_login, name='register_and_login'),
    path('dogs/<int:pk>/', DogDetailView.as_view(), name='dog_details'),
    path('shelters/<int:pk>/', ShelterDetailView.as_view(), name='shelter_details'),
    path('create-post/', create_post, name='create_post'),
    path('shelter/edit/<int:pk>/', edit_shelter, name='edit_shelter'),
    path('dogs/edit/<int:pk>/', EditDogPostView.as_view(), name='edit_post'),
    path('delete-post/<int:post_id>/', delete_post, name='delete_post'),
    path('archive/', archive_page, name='archive_page'),
    path('dogs/<int:pk>/comment/', create_comment, name='add_comment_to_post'),
    path('dogs/<int:post_pk>/comments/<int:comment_pk>/edit/', views.edit_comment, name='edit_comment'),
    path('dogs/<int:post_pk>/comments/<int:comment_pk>/delete/', views.delete_comment, name='delete_comment'),
    path('notifications/', views.user_notifications, name='notifications'),
    path('notifications/mark-as-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('subscribe/<int:post_id>/', views.subscribe_to_post, name='subscribe'),
    path('unsubscribe/<int:post_id>/', views.unsubscribe_from_post, name='unsubscribe'),
]
