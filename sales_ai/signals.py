# your_app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase
from .tasks import retrain_prophet_model

@receiver(post_save, sender=Purchase)
def retrain_model_on_purchase(sender, instance, created, **kwargs):
    if created:
        retrain_prophet_model.delay(instance.customer.id)
