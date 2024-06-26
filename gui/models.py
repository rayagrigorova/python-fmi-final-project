from django.contrib.auth import get_user_model
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
    # Link the shelter model to the 'shelter' user type. related_name='shelter' is added so the shelter related to
    # the user can be accessed with 'user.shelter'. limit_choices_to guarantees that the only type of users to be
    # linked to a Shelter instance will be 'shelter' users.
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='shelter',
                                limit_choices_to={'role': 'shelter'}, null=True)
    name = models.CharField(max_length=255)
    working_hours = models.TextField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('details', kwargs={'pk': self.pk})


class DogAdoptionPost(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    ADOPTION_STAGE_CHOICES = [
        ('active', 'Active'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    breed = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='dogs/', blank=True, null=True)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default='M')
    adoption_stage = models.CharField(max_length=20, choices=ADOPTION_STAGE_CHOICES, default='active')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('details', kwargs={'pk': self.pk})


class Comment(models.Model):
    post = models.ForeignKey(DogAdoptionPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content


class PostSubscription(models.Model):
    """ Allow users to follow posts that have a status of "in progress"
    and receive a notification when the status changes to 'active' """

    # 'related_name' specifies the name of the reverse relation from a related model
    # (by default it would be postsubscription_set).
    # 'related_name' makes it possible to access all subscriptions of a user (using user.subscriptions.all())
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='subscriptions')
    post = models.ForeignKey(DogAdoptionPost, on_delete=models.CASCADE, related_name='subscribers')
    is_active = models.BooleanField(default=True)


class Notification(models.Model):
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_post = models.ForeignKey(DogAdoptionPost, on_delete=models.CASCADE, related_name='notifications', null=True)

    def __str__(self):
        return f'Notification recipient: {self.recipient.username} content: {self.message}'
