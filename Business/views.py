from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .makePayment import make_payment
from django.utils import timezone
from datetime import datetime
import re
from .serializers import *
from .models import *
from dotenv import load_dotenv
import os
# Create your views here.

class MpesaConfirmation(APIView):
    def post(self, request):
        print('M-PESA CONFIRMATION CALLBACK:', request.data)

        checkout_request_id = request.data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")
        result_code = request.data.get("Body", {}).get("stkCallback", {}).get("ResultCode")

        try:
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        except MpesaTransaction.DoesNotExist:
            return Response({"message": "Transaction not found"}, status=404)

        if result_code == 0:
            # ✅ Success — update business
            transaction.status = "success"
            business = transaction.business
            business.subscription_plan = transaction.plan
            business.subscription_plan_expiry = timezone.now() + timezone.timedelta(days=30 * transaction.months)
            business.save()
        else:
            transaction.status = "failed"

        transaction.save()
        return Response({"message": "Callback received"}, status=200)



class BusinessSubscription(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        load_dotenv()
        
        print('request data ', request.data)
        phone = request.data.get('paymentNumber')
        raw_data = request.data.dict()

        if phone:
            phone = phone.strip()
            if re.fullmatch(r'^254\d{9}$', phone):
                normalized_phone = phone
            elif re.fullmatch(r'^0\d{9}$', phone):
                normalized_phone = '254' + phone[1:]
            else:
                return Response(
                    {"error": "Invalid phone number format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Use normalized_phone moving forward
        print("Validated phone:", normalized_phone)


        # Extract keys that look like 'months[PlanName]'
        months_selected = {}
        for key, value in raw_data.items():
            if key.startswith("months[") and key.endswith("]"):
                plan_name = key[7:-1]  # strip "months[" and "]"
                months_selected[plan_name] = int(value)

        subscription_months = months_selected[plan_name]
        try:
            plan = SubScriptionOptions.objects.get(pk=pk)
            plan_amount = int(plan.price)
            amount_payable = plan_amount * int(subscription_months)
            print('amount payable is ', amount_payable)
        except SubScriptionOptions.DoesNotExist:
            return Response({"message": "Subscription plan not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            business = BusinessDetails.objects.get(owner=request.user)
            print('business ', business)
        except BusinessDetails.DoesNotExist:
            return Response({"message": "No business found"}, status=status.HTTP_404_NOT_FOUND)
        

        # business = business.first()
        # print('business agaon ', business)
        print('running here...')
        # if business.subscription_plan:
        print('but not here')
        if business.subscription_plan_expiry and business.subscription_plan_expiry > timezone.now():
            return Response({"message": "You already have a subscription plan"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # make_payment(normalized_phone, amount_payable)
            result = make_payment(normalized_phone, amount_payable)

            if not result['success']:
                return Response({"message": "Payment initiation failed", "error": result['error']}, status=400)
            
            transaction = MpesaTransaction.objects.create(
                business=business,
                phone=normalized_phone,
                amount=amount_payable,
                plan=plan,
                months=subscription_months,
                checkout_request_id=result["CheckoutRequestID"]
            )

            return Response({"message": "Payment initiated. Awaiting confirmation."}, status=200)


            # If the subscription plan has expired, update it
            business.subscription_plan = plan
            business.subscription_plan_expiry = timezone.now() + timezone.timedelta(days=30 * subscription_months)
            business.save()
            return Response({"message": "Subscription plan updated successfully"}, status=status.HTTP_200_OK)
        # else:
        #     print("eligible for a free trial ")
        #     return Response({"message":"eligible for free trial"})
        
       

class BusinessManagement(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        plan = SubScriptionOptions.objects.all()
        serialized = SubsriptionsSerializers(plan, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    

    


class BusinessOperation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            business = BusinessDetails.objects.get(owner=request.user)
        except BusinessDetails.DoesNotExist:
            return Response({"message": "No business found"}, status=status.HTTP_404_NOT_FOUND)
        serialized = BusinessDetailsSerializer(business,  context={'request': request})
        
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        print('owner ', request.user)
        print('request data ', request.data)
        serializer = BusinessDetailsSerializer(data=request.data)
        if serializer.is_valid():
            business = serializer.save(owner=request.user)
            request.user.business = business
            request.user.save(update_fields=["business"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class SubscriptionPaymentsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        subs = SubScriptionPayment.objects.filter(pk=pk)
        serial = SubscriptionPaymentsSerializer(subs, many=True)

        return Response(serial.data, status=status.HTTP_200_OK)
    


class BusinessSubscriptionFreeTrial(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        try:
            business = BusinessDetails.objects.get(owner=request.user)
        except BusinessDetails.DoesNotExist:
            return Response({"message": "No business found"}, status=status.HTTP_404_NOT_FOUND)

        if business.is_trial_active():
            return Response({"message": "Free trial already active"}, status=status.HTTP_400_BAD_REQUEST)

        plan = SubScriptionOptions.objects.get(pk=pk)
        business.start_trial()
        business.subscription_plan = plan
        business.save()

        return Response({"message": "Free trial activated successfully"}, status=status.HTTP_200_OK)