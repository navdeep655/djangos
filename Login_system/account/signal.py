from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import profile_data,Product
from django.contrib.auth.models import User
import os

@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        profile_data.objects.create(user=instance)


@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    # Image hai?
    if instance.image:
        # File exist karti hai?
        if os.path.isfile(instance.image.path):
            # Delete karo!
            os.remove(instance.image.path)