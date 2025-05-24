from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Employees, SalesTab
from django.dispatch import receiver
from sales_ai.tasks import retrain_prophet_model
from sales_ai.models import SalesReport, SalesByPersonReport
from datetime import date

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





@receiver(post_save, sender=SalesTab)
def trigger_ai_training(sender, instance, created, **kwargs):
    print('calling this signal!', created)
    if created:
        retrain_prophet_model.delay(instance.customer.id)



@receiver(post_save, sender=SalesTab)
def save_sales_analysis(sender, instance, created, **kwargs):
    if created:
        report, created = SalesReport.objects.get_or_create(
            business=instance.business,
            sales_team=instance.sales_team,
            sales_choice=instance.sales_choice,
            date = date.today(),
            # defaults={'sales_quantity': instance.quantity}
            defaults={
                'sales_quantity': instance.quantity,
                'total_amount': instance.total_amount or 0,
                'cash_amount': instance.cashAmount or 0,
                'mpesa_amount': instance.mpesaAmount or 0
            }
        )

    if not created:
            report.sales_quantity += instance.quantity
            report.total_amount += instance.total_amount or 0
            report.cash_amount += instance.cashAmount or 0
            report.mpesa_amount += instance.mpesaAmount or 0
            report.save()

    person_report, created = SalesByPersonReport.objects.get_or_create(
            business=instance.business,
            sales_person=instance.sales_person,
            product=instance.store_product,
            sales_choice=instance.sales_choice,
            date=date.today(),
            defaults={
                'quantity': instance.quantity,
                'total_amount': instance.total_amount or 0,
                'cash_amount': instance.cashAmount or 0,
                'mpesa_amount': instance.mpesaAmount or 0,
            }
        )

    if not created:
        person_report.quantity += instance.quantity
        person_report.total_amount += instance.total_amount or 0
        person_report.cash_amount += instance.cashAmount or 0
        person_report.mpesa_amount += instance.mpesaAmount or 0
        person_report.save()