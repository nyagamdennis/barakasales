from rest_framework import serializers
from .models import *



class FeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = '__all__'

class SubsriptionsSerializers(serializers.ModelSerializer):
    features = FeaturesSerializer(many=True, read_only=True)
    class Meta:
        model = SubScriptionOptions
        fields = '__all__'


class BusinessDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDetails
        fields = '__all__'