from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Shelter


@receiver(post_save, sender=CustomUser)
def create_shelter_for_new_shelter_user(sender, instance, created, **kwargs):
    if created and instance.role == 'shelter':
        Shelter.objects.create(user=instance)
