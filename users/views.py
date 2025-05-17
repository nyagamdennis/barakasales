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
from rest_framework_simplejwt.views import TokenRefreshView


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
        # token['role'] = get_user_role(user)
        token['is_owner'] = getattr(user, 'is_owner', False)
        token['is_employee'] = getattr(user, "is_employee", False)



        # Include employeeId if user is_employee
        if getattr(user, 'is_employee', False):
            try:
                employee = Employees.objects.get(user=user)
                token['employee_id'] = employee.id
                # token['employee_verified'] = employee.verified
            except Employees.DoesNotExist:
                token['employee_id'] = None
                # token['employee_verified'] = False



        if hasattr(user, 'business') and user.business:
            plan = user.business.subscription_plan
            token['business'] = {
                'id': user.business.id,
                'name': user.business.name,
                # 'plan': user.business.subscription_plan,
                'plan': {
            'id': plan.id,
            'name': plan.name,
            'price': plan.price,
            'employee_limit': plan.employee_limit,
        } if plan else None,
                'created_at': user.business.created_at.isoformat() if user.business.created_at else None
            }
        else:
            token['business'] = None
        
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
    
    
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
    


@api_view(['GET'])
def users(request):
    user = CustomUser.objects.all()
    serialize = UserSerializer(user, many = True)
    return Response(serialize.data)



@api_view(['POST'])
def user_registration(request):
    business_id = request.data.get("businessId")
    email = request.data.get("email")
    phone = request.data.get("phone_number")

   
    business = BusinessDetails.objects.get(id=business_id) if business_id else None

    if business:
        employees_limit = business.subscription_plan.employee_limit
        business_employees = Employees.objects.filter(business=business_id)
        Number_of_employees = business_employees.count()

        if Number_of_employees >= employees_limit:
            return Response({"error": "Employee limit reached. Please consult your boss."}, status=400)


    # ✅ Check if user already exists by email or phone
    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "A user with this email already exists."}, status=400)
    if CustomUser.objects.filter(phone_number=phone).exists():
        return Response({"error": "A user with this phone number already exists."}, status=400)


    context = {
        "is_employee": bool(business_id),
        "is_owner": not bool(business_id),
        "business_id": business_id,
    }
    print('context is ', context)

    serializer = UserSerializer(data=request.data, context=context)
    if serializer.is_valid():
        user = serializer.save()
        if business_id:
            Employees.objects.create(
                user=user,
                business=business,
                phone=user.phone_number
            )

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