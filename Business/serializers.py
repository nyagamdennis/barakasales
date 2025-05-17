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
        fields = ['id', 'name','price','description','features', 'employee_limit','highlight']


class BusinessDetailsSerializer(serializers.ModelSerializer):
    subscription_plan = SubsriptionsSerializers(read_only=True)


    is_expired = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    is_trial = serializers.SerializerMethodField()
    trial_ends_in = serializers.SerializerMethodField()
    class Meta:
        model = BusinessDetails
        fields = [
            'id',
            'owner',
            'name',
            'business_logo',
            'created_at',
            'subscription_period',
            'subscription_plan',
            'subscription_plan_expiry',
            'subscription_payment',
            'is_expired',
            'days_remaining',
            'is_trial',
            'trial_ends_in'
        ]



    def get_is_expired(self, obj):
        if obj.subscription_plan_expiry:
            print('timezone now', timezone.now())
            print('subscription plan expiry', obj.subscription_plan_expiry)
            return timezone.now() > obj.subscription_plan_expiry
        return True

    def get_days_remaining(self, obj):
        if obj.subscription_plan_expiry:
            delta = obj.subscription_plan_expiry - timezone.now()
            return max(delta.days, 0)
        return 0

    def get_is_trial(self, obj):
        return obj.is_trial_active()

    def get_trial_ends_in(self, obj):
        if obj.is_trial and obj.trial_end:
            delta = obj.trial_end - timezone.now()
            return max(delta.days, 0)
        return None


    
class SubscriptionPaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubScriptionPayment
        fields = '__all__'