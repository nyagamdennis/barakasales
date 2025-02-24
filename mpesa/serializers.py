from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from users.serializers import UserSerializer
from collections import defaultdict
from datetime import datetime
from decimal import Decimal


class MpesaMessagesSerializers(serializers.ModelSerializer):
    class Meta:
        model = MpesaMessages
        fields = '__all__'


    def validate_date(self, value):
        """Ensure date is in the correct format (YYYY-MM-DD) and convert if needed."""
        if isinstance(value, str):  # If date is a string, convert it
            try:
                return datetime.strptime(value, "%d/%m/%y").date()  # Convert DD/MM/YY to YYYY-MM-DD
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use DD/MM/YY.")
        elif isinstance(value, datetime):  # If already a date object, return as is
            return value.date()
        return value  # If it's already in correct format, return as is
    
    def validate_amount(self, value):
        """Ensure amount is a valid decimal, handling comma formatting."""
        if isinstance(value, str):  # Check if value is string before replacing
            value = value.replace(",", "")  # Remove commas from '1,000.00'
        try:
            return Decimal(value)  # Convert to Decimal
        except:
            raise serializers.ValidationError("Invalid amount format.")