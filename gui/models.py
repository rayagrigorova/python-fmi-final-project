from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ordinary', 'Ordinary User'),
        ('shelter', 'Shelter'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ordinary')
    registration_code = models.CharField(max_length=100, blank=True, null=True)
