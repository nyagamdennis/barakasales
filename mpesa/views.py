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
        print('data is ', request.data)
        if isinstance(request.data, list):  # Check if data is a list
            serializer = MpesaMessagesSerializers(data=request.data, many=True)
        else:
            serializer = MpesaMessagesSerializers(data=[request.data], many=True)  # Convert single item to a list

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"{len(serializer.data)} transactions saved successfully!", "data": serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        print('error is ', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)