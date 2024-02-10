from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ordinary', 'Ordinary User'),
        ('shelter', 'Shelter'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ordinary')
    registration_code = models.CharField(max_length=100, blank=True, null=True)


class RegistrationCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_activated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} ({'Activated' if self.is_activated else 'Inactive'})"
