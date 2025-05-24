# sales_ai/urls.py

from django.urls import path
from .views import PredictNextPurchase, SalesReportViews, CompanyExpensesView

urlpatterns = [
    path('predict/<str:customer_id>/', PredictNextPurchase.as_view(), name='predict-next'),
    path('sales-analysis/', SalesReportViews.as_view()),
    path('company-expenses/', CompanyExpensesView.as_view()),
    path('company-expenses/<str:pk>/', CompanyExpensesView.as_view())
]
