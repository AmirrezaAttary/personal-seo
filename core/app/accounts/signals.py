import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_delete, sender=Profile)
def delete_profile_image(sender, instance, **kwargs):
    if instance.image and instance.image.name != 'default/default-profile.webp':
        image_path = instance.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)

@receiver(pre_save, sender=Profile)
def delete_old_profile_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        # اگر این یک شی جدید است و قبلا وجود نداشته، کاری نمی‌کنیم
        return

    try:
        old_instance = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image != new_image and old_image.name != 'default/default-profile.webp':
        old_image_path = old_image.path
        if os.path.isfile(old_image_path):
            os.remove(old_image_path)
