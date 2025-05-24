# sales_ai/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Purchase, Prediction
from .prophet_utils import train_and_forecast
import pandas as pd
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from Business.models import BusinessDetails
from .serializers import *

class PredictNextPurchase(APIView):
    def get(self, request, customer_id):
        purchases = Purchase.objects.filter(customer_id=customer_id).order_by('date')
        if not purchases.exists():
            return Response({"error": "No purchase data found."}, status=status.HTTP_404_NOT_FOUND)
        
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



class SalesReportViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        business = BusinessDetails.objects.get(owner=request.user)
        data = SalesReport.objects.filter(business=business)

        serialize = SalesReportSerializer(data, many=True)

        return Response(serialize.data, status=status.HTTP_200_OK)



class RefillReportAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        business = BusinessDetails.objects.get(owner=request.user)
        data = RefillCostAnalysis.objects.filter(business=business)

        serialize = RefillCostAnalysisSerializer(data, many=True)

        return Response(serialize.data, status=status.HTTP_200_OK)
    

class CompanyExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        business = BusinessDetails.objects.get(owner = request.user)

        data = CompanyExpenses.objects.filter(business=business).order_by('-date')

        serializer = CompanyExpensesSerializer(data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        business =  BusinessDetails.objects.get(owner =  request.user)

        data =  request.data.copy()
        data['business'] = business.id
        serialize =  CompanyExpensesSerializer(data= data, context= {"request":request})

        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, pk):
        try:
            expense = CompanyExpenses.objects.get(pk=pk)
        except CompanyExpenses.DoesNotExist:
            return Response({"error":"no expense found."}, status=status.HTTP_404_NOT_FOUND)
        
        expense.delete()
        return Response({"successfully delete."}, status=status.HTTP_200_OK)
    

    def patch(self, request, pk):
        try:
            expense = CompanyExpenses.objects.get(pk=pk)
        except CompanyExpenses.DoesNotExist:
            return Response({"error":"Expense not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serialize = CompanyExpensesSerializer(expense, data = request.data, partial=True)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)