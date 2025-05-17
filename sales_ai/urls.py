# sales_ai/urls.py

from django.urls import path
from .views import PredictNextPurchase

urlpatterns = [
    path('predict/<int:customer_id>/', PredictNextPurchase.as_view(), name='predict-next'),
]
