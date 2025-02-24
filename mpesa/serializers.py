from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from users.serializers import UserSerializer
from collections import defaultdict


class MpesaMessagesSerializers(serializers.ModelSerializer):
    class Meta:
        model = MpesaMessages
        fields = '__all__'