from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

# Create your views here.

class BusinessManagement(APIView):
    def get(self, request):
        plan = SubScriptionOptions.objects.all()
        serialized = SubsriptionsSerializers(plan, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    


class BusinessOperation(APIView):
    def get(self, request):
        business = BusinessDetails.objects.all()
        serialized = BusinessDetailsSerializer(business, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)