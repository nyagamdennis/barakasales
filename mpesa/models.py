from django.db import models

# Create your models here.


class MpesaMessages(models.Model):
    transaction_code = models.CharField(max_length=200)
    amount = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self) -> str:
        return self.name