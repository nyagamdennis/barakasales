# yourapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Employees

@receiver(post_save, sender=Employees)
def broadcast_employee_verification(sender, instance, **kwargs):
    if instance.verified:  # only broadcast if verified
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"employee_status_{instance.id}",  # group name
            {
                "type": "send_verification_status",
                "verified": instance.verified
            }
        )
