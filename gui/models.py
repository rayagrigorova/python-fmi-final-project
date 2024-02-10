from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


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


class Shelter(models.Model):
    name = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('details', kwargs={'pk': self.pk})


class DogAdoptionPost(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    breed = models.CharField(max_length=255)
    description = models.TextField()
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dogs/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('details', kwargs={'pk': self.pk})
