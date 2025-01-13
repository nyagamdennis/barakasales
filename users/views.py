from django.shortcuts import render
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from BarakaApp.models import *
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


# Create a custom employee permission
def add_employee_permission():
    content_type = ContentType.objects.get_for_model(CustomUser)
    Permission.objects.get_or_create(
        codename="is_employee",
        name="Employee Status",
        content_type=content_type,
    )


def get_user_role(user):
    print("Has employee permission:", user.has_perm("users.is_employee"))
    if user.is_superuser:
        return "admin"
    elif user.has_perm("users.is_employee") and user.is_active:
        return "employee"
    elif user.is_active:
        return "regular_user"
    return "inactive_user"



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):   
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['id'] = user.id
        token['role'] = get_user_role(user)
        return token
    
    
    
    def validate(self, attrs):
        email_or_phone = attrs.get('email')
        password = attrs.get('password')
        

        if '@' in email_or_phone:
            user = CustomUser.objects.filter(email=email_or_phone).first()
        else:
            user = CustomUser.objects.filter(phone_number=email_or_phone).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return data
    
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
    


@api_view(['GET'])
def users(request):
    user = CustomUser.objects.all()
    serialize = UserSerializer(user, many = True)
    return Response(serialize.data)



@api_view(['POST'])
def user_registration(request):
    serializer = UserSerializer(data=request.data)
    print('Users data ', request.data)
    if serializer.is_valid():
        user = serializer.save()
        response_data = {
            'message': 'User registered successfully!',
            'user': serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    print('error' ,serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TransferUser(APIView):
    def post(self, request):
        employee_id = request.data.get("employeeId")
        new_team_id = request.data.get("teamId")

        try:
            # Fetch the employee and the new team
            employee = Employees.objects.get(id=employee_id)
            new_team = SalesTeam.objects.get(id=new_team_id)

            # Remove the employee from all current teams (Many-to-Many relationship)
            existing_teams = SalesTeam.objects.filter(employees=employee)
            for team in existing_teams:
                team.employees.remove(employee)

            # Add the employee to the new team
            new_team.employees.add(employee)

            return Response({
                "message": f"Employee {employee.first_name} {employee.last_name} has been migrated to {new_team.name}."
            }, status=status.HTTP_200_OK)

        except Employees.DoesNotExist:
            return Response({'error': 'Employee does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except SalesTeam.DoesNotExist:
            return Response({'error': 'Sales team does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
