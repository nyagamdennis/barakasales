from django.db import models
from rest_framework_api_key.models import AbstractAPIKey
import datetime
from django.utils import timezone
from datetime import timedelta
# from users.models import CustomUser


# Create your models here.

class Features(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SubScriptionOptions(models.Model):
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    description = models.TextField()
    features = models.ManyToManyField(Features)
    employee_limit = models.IntegerField(default=5)
    highlight = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class SubScriptionPayment(models.Model):
    owner = models.OneToOneField('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    # business = models.ForeignKey(BusinessDetails, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_plan = models.ForeignKey(SubScriptionOptions, on_delete=models.SET_NULL, null=True, blank=True)
    payment_number = models.CharField(max_length=12)
    subscription_start = models.DateTimeField()
    subscription_end = models.DateTimeField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.subscription_plan.name
    


class BusinessDetails(models.Model):
    owner = models.OneToOneField('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name="business_user")
    name = models.CharField(max_length=200)
    business_logo = models.ImageField(upload_to="logos", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    subscription_period = models.PositiveIntegerField(default=1)
    subscription_plan = models.ForeignKey(SubScriptionOptions, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_plan_expiry = models.DateTimeField(null=True, blank=True)
    subscription_payment = models.ForeignKey(SubScriptionPayment, on_delete=models.SET_NULL, null=True, blank=True)



    # 🚀 New fields for free trial
    is_trial = models.BooleanField(default=False)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)

    def start_trial(self):
        """Call this method to activate a 10-day trial"""
        if not self.is_trial:
            now = timezone.now()
            self.is_trial = True
            self.trial_start = now
            self.trial_end = now + timedelta(days=10)
            self.subscription_plan_expiry = self.trial_end
            self.save()

    def is_trial_active(self):
        if self.is_trial and self.trial_end:
            return timezone.now() <= self.trial_end
        return False

    def has_active_subscription(self):
        """Check if a business is subscribed either via paid plan or trial"""
        return (self.subscription_plan and self.subscription_plan_expiry and timezone.now() < self.subscription_plan_expiry) or self.is_trial_active()

    def __str__(self):
        return self.name
    


    def __str__(self):
        return self.name




class BusinessAPIKey(AbstractAPIKey):
    business = models.ForeignKey(
        BusinessDetails,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )




# models.py
class MpesaTransaction(models.Model):
    business = models.ForeignKey(BusinessDetails, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    amount = models.IntegerField()
    plan = models.ForeignKey(SubScriptionOptions, on_delete=models.CASCADE)
    months = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='pending')
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)