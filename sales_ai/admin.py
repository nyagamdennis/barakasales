from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(Customer)
admin.site.register(Purchase)
admin.site.register(Prediction)
admin.site.register(SalesByPersonReport)
admin.site.register(SalesReport)
admin.site.register(RefillCostAnalysis)
admin.site.register(CompanyExpenses)