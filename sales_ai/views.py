# sales_ai/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Purchase, Prediction
from .prophet_utils import train_and_forecast
import pandas as pd

class PredictNextPurchase(APIView):
    def get(self, request, customer_id):
        purchases = Purchase.objects.filter(customer_id=customer_id).order_by('date')
        if not purchases.exists():
            return Response({"error": "No purchase data found."}, status=404)
        
        df = pd.DataFrame({
            'ds': [p.date for p in purchases],
            'y': [float(p.amount) for p in purchases],
        })
        
        forecast = train_and_forecast(df, periods=30)
        next_date = forecast['ds'].iloc[-1]
        
        return Response({
            "customer_id": customer_id,
            "predicted_next_purchase_date": next_date
        })
    

class GetStoredPrediction(APIView):
    def get(self, request, customer_id):
        try:
            prediction = Prediction.objects.filter(customer_id=customer_id).latest("created_at")
            return Response({
                "customer_id": customer_id,
                "predicted_next_purchase_date": prediction.predicted_date
            })
        except Prediction.DoesNotExist:
            return Response({"error": "No prediction available"}, status=404)
