from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Employees


@receiver(post_save, sender=Employees)
def broadcast_employee_status(sender, instance, created, **kwargs):
    # Only broadcast if the verified field changed
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"employee_status_{instance.id}",
            {
                "type": "send_verification_status",
                "verified": instance.verified  # ✅ use the actual value
            }
        )
