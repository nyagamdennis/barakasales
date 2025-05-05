from django.db import models

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
    highlight = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BusinessDetails(models.Model):
    name = models.CharField(max_length=200)
    business_logo = models.ImageField(upload_to="logos")
    date_created = models.DateTimeField(auto_now_add=True)
    Subsription_plan = models.ForeignKey(SubScriptionOptions, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name