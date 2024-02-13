from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Shelter


# 'post_save' is a signal Django sends after a model's 'save' method is called
# The @receiver decorator registers the function as a signal handler.
@receiver(post_save, sender=CustomUser)
def create_shelter_for_new_shelter_user(sender, instance, created, **kwargs):
    # Check if the CustomUser instance was just created and if it's a shelter
    if created and instance.role == 'shelter':
        # Create a Shelter object for the respective user
        Shelter.objects.create(user=instance)
