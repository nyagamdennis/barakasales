from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from .models import *
from Business.models import *
from .serializers import *
from rest_framework.views import APIView




# Create your views here.
class SubriptionPayment(APIView):
    def post(self, request, pk):
        subscription_plan = request.data.get('plan')
        phone_number = request.data.get('phone_number')
        business = request.data.get('business')

        try:
            subpription = SubScriptionOptions.objects.get(pk=subsciption_plan)
        except SubScriptions.DoesNotExist:
            return Response('Select a valid subscription.')

        # try:
        #     employee = Employees.objects.get(user__id=user_id.id)
        #     sales_team = employee.sales_team.id
        # except Employees.DoesNotExist:
        #     sales_team = None
        return Response('sueccess')


class mpesatransactions(APIView):
    def get(self, request):
        sms = MpesaMessages.objects.all()

        serialize = MpesaMessagesSerializers(sms, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        if not isinstance(request.data, list):  
            return Response({"error": "Expected a list of transactions"}, status=status.HTTP_400_BAD_REQUEST)

        processed_data = []
        duplicate_count = 0
        new_count = 0

        for item in request.data:
            try:
                # Ensure all required fields exist
                if not all(key in item for key in ["transactionCode", "amount", "senderName", "phoneNumber", "date"]):
                    return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

                # Convert date format (DD/MM/YY → YYYY-MM-DD)
                date_obj = datetime.strptime(item["date"], "%d/%m/%y").date()
                formatted_date = date_obj.strftime("%Y-%m-%d")

                # Remove commas from amount
                cleaned_amount = item["amount"].replace(",", "")

                # Check for duplicate transaction
                if MpesaMessages.objects.filter(transaction_code=item["transactionCode"]).exists():
                    duplicate_count += 1
                    continue  # Skip saving

                processed_data.append({
                    "transaction_code": item["transactionCode"],
                    "amount": cleaned_amount,
                    "name": item["senderName"],
                    "phone": item["phoneNumber"],
                    "date": formatted_date
                })
                new_count += 1

            except ValueError as e:
                return Response({"error": f"Invalid data format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure a response is always returned
        if processed_data:
            serializer = MpesaMessagesSerializers(data=processed_data, many=True)
            if serializer.is_valid():
                serializer.save()

        return Response(
            {"message": f"{new_count} new transactions saved, {duplicate_count} duplicates skipped."},
            status=status.HTTP_201_CREATED
        )