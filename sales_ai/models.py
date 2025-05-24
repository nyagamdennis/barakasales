# sales_ai/models.py

from django.db import models
from django.contrib.auth.models import User
from BarakaApp.models import Customers, SalesTeam, CylinderStore, CylinderWeight
from Business.models import BusinessDetails
from users.models import CustomUser



class Purchase(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


class Prediction(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    predicted_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)



class SalesReport(models.Model):
    WHOLESALE = "WHOLESALE"
    RETAIL = "RETAIL"

    SALES_CHOICES = [
        (WHOLESALE, "Wholesale"),
        (RETAIL, "Retail"),
    ]
    business = models.ForeignKey(BusinessDetails, on_delete=models.SET_NULL, null=True, blank=True)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.SET_NULL, null=True, blank=True)
    sales_choice = models.CharField(choices=SALES_CHOICES, max_length=20, null=True, blank=True)  # ✅ new field
    sales_quantity = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)       # ✅ new
    cash_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)        # ✅ new
    mpesa_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)       # ✅ new
    date = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.sales_team.name} - {self.sales_choice} - {self.date}: {self.sales_quantity}"
    


class SalesByPersonReport(models.Model):
    business = models.ForeignKey(BusinessDetails, on_delete=models.SET_NULL, null=True, blank=True)
    sales_person = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(CylinderStore, on_delete=models.SET_NULL, null=True, blank=True)
    sales_choice = models.CharField(max_length=20, choices=[("WHOLESALE", "Wholesale"), ("RETAIL", "Retail")])
    quantity = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mpesa_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField()

    def __str__(self):
        return f"{self.sales_person} - {self.product} - {self.date}"




class RefillCostAnalysis(models.Model):
    business = models.ForeignKey(BusinessDetails, on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.ForeignKey(CylinderWeight, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    total_cost = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.business} | {self.weight} | {self.date} → {self.quantity} pcs"




class CompanyExpenses(models.Model):
    business = models.ForeignKey(BusinessDetails, on_delete=models.SET_NULL, null=True, blank=True)
    expense_name = models.CharField(max_length=200)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

