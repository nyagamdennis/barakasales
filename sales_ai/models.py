# sales_ai/models.py

from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    name = models.CharField(max_length=100)

class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

class Prediction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    predicted_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)