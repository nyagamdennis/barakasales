from django.db import models

# Create your models here.


class MpesaMessages(models.Model):
    transaction_code = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    def __str__(self) -> str:
        return self.name