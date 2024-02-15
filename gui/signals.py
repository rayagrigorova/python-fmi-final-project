from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import CustomUser, Shelter, DogAdoptionPost, Notification
from django.db.models.signals import pre_save

# 'post_save' is a signal Django sends after a model's 'save' method is called
# The @receiver decorator registers the function as a signal handler.
@receiver(post_save, sender=CustomUser)
def create_shelter_for_new_shelter_user(sender, instance, created, **kwargs):
    # Check if the CustomUser instance was just created and if it's a shelter
    if created and instance.role == 'shelter':
        # Create a Shelter object for the respective user
        Shelter.objects.create(user=instance)


@receiver(pre_save, sender=DogAdoptionPost)  # The function will be called right before a DogAdoptionPost is saved
def notify_subscribers_on_status_change(sender, instance, **kwargs):
    # If instance has a primary key it exists in the database (it was already saved in the database)
    if instance.pk:
        try:
            previous = DogAdoptionPost.objects.get(pk=instance.pk)

            if previous.adoption_stage == 'in_process' and instance.adoption_stage == 'active':
                # Get all subscriptions for the post (pairs of user-post, along with a boolean value to check for activation)
                all_post_subscriptions = instance.subscribers.all()
                post_url = reverse('dog_details', kwargs={'pk': instance.pk})

                for subscription in all_post_subscriptions:
                    Notification.objects.create(
                        recipient=subscription.user,
                        message=f'{instance.name} is available for adoption. View details here: {post_url}'
                    )
        except DogAdoptionPost.DoesNotExist:
            pass

