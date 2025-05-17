from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from BarakaApp.models import Employees
import jwt
from django.conf import settings



class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Decode the refresh token to get the user ID
        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh['user_id']
        
        # Get current user
        user = CustomUser.objects.get(id=user_id)

        # Add fresh user data to access token
        access_token = RefreshToken(attrs['refresh']).access_token
        access_token['email'] = user.email
        access_token['id'] = user.id
        # access_token['role'] = 'admin' if user.is_superuser else (
        #     'employee' if user.is_employee else 'regular_user'
        # )
        access_token['is_owner'] = user.is_owner
        access_token['is_employee'] = user.is_employee
        access_token['business'] = user.business_id if user.business else None

        if user.is_employee:
            try:
                employee = Employees.objects.get(user=user)
                access_token['employee_id'] = employee.id
                # access_token['employee_verified'] = employee.verified
            except Employees.DoesNotExist:
                access_token['employee_id'] = None
                # access_token['employee_verified'] = False

        



        data['access'] = str(access_token)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print('user context data', self.context)
        
        is_employee = self.context.get('is_employee', False)
        is_owner = self.context.get('is_owner', False)
        business_id = self.context.get('business_id')

        # Create user object but don't save yet
        user = CustomUser(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            is_employee=is_employee,
            is_owner=is_owner,
        )
        user.set_password(validated_data['password'])

        

        user.save()
        print('user created', user)
        return user

   