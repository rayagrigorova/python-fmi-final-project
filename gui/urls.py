from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import register
from .views import register_and_login

urlpatterns = [
    path('', views.index, name='index'),
    path('login', auth_views.LoginView.as_view(), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('register/', register, name='register'),
    path('register-login/', register_and_login, name='register_and_login'),
]
