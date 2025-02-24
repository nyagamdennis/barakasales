from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.views import APIView




# Create your views here.


class mpesatransactions(APIView):
    def get(self, request):
        sms = MpesaMessages.objects.all()

        serialize = MpesaMessagesSerializers(sms, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        if not isinstance(request.data, list):  
            return Response({"error": "Expected a list of transactions"}, status=status.HTTP_400_BAD_REQUEST)

        processed_data = []
        for item in request.data:
            try:
                # Ensure all fields exist in each transaction
                if not all(key in item for key in ["transactionCode", "amount", "senderName", "phoneNumber", "date"]):
                    return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

                # Convert 'date' from 'DD/MM/YY' to 'YYYY-MM-DD'
                date_obj = datetime.strptime(item["date"], "%d/%m/%y").date()
                formatted_date = date_obj.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD'

                # Remove commas from amount (e.g., '1,000.00' -> '1000.00')
                cleaned_amount = item["amount"].replace(",", "")

                processed_data.append({
                    "transaction_code": item["transactionCode"],
                    "amount": cleaned_amount,
                    "name": item["senderName"],
                    "phone": item["phoneNumber"],
                    "date": formatted_date
                })

            except ValueError as e:
                return Response({"error": f"Invalid data format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MpesaMessagesSerializers(data=processed_data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"{len(serializer.data)} transactions saved successfully!", "data": serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)