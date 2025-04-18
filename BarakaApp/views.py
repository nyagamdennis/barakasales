from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import *
from .serializers import *
import africastalking
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from users.models import CustomUser
from datetime import date





def smsSender(users, message):
    username = "Kibaki"    # use 'sandbox' for development in the test environment
    api_key = "081476f218d28a1a680a78086d13efa2d3e94044433f2c743dbc15db302d57b1"      # use your sandbox app API key for development in the test environment
    africastalking.initialize(username, api_key)


    # Initialize a service e.g. SMS
    sms = africastalking.SMS
    # Use the service synchronously
    response = sms.send(message, users)



def my_date(date_str):
    date_object = datetime.strptime(date_str, '%d-%m-%Y').date()

    return date_object



@api_view(['GET'])
def customers(request):
    customer = Customers.objects.order_by('-date_aded')
    customerserialize = Customerserializer(customer, many=True)
    
    return Response(customerserialize.data)


@api_view(['GET'])
def debtors(request):
    depts = Dbts.objects.filter(cleared = False).order_by('-date_given')
    debtorserialize = Debtorsserializer(depts, many=True)
    
    return Response(debtorserialize.data)


@api_view(['GET'])
def sales_func(request):
    sales = SalesTab.objects.all()
    sales_serialize = SaleSerializer(sales, many=True)
    
    return Response(sales_serialize.data)


@api_view(['GET'])
def location_func(request):
    location = Locations.objects.all()
    location_serialize = CustomerLocationSerializer(location, many=True)
    
    return Response(location_serialize.data)


@api_view(['GET'])
def product_func(request):
    product = Cylinder.objects.all()
    product_serialize = CylinderSerializer(product, many=True)
    
    return Response(product_serialize.data)


@api_view(['POST', 'PUT'])
def add_customer(request):
    if request.method == 'POST':
        
        serializer = AddCustomerSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_sales(request):
    if request.method != 'POST':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if request.method == 'POST':
       
        user_id = request.user
        custom_user_id = user_id.id
        

        # Get the user's sales team
        try:
            employee = Employees.objects.get(user__id=user_id.id)
            sales_team = employee.sales_team.id
        except Employees.DoesNotExist:
            sales_team = None

        formdata = {}
        user_id = request.user.id
        myDict = request.data

        # Customer and Sale Info
        
        
        customer = myDict.get('customer', {})
        type_of_sale = customer.get('sales', '')

        # Assign default customer details if not provided
        name = customer.get('name', '')
        phone = customer.get('phone', None)
        location = customer.get('location', {}).get('name', '')

        if not name  or not location:
            if type_of_sale == "RETAIL":
                customer['name'] = 'no_name'
                customer['phone'] = '0700000000'
                # customer['location'] = 'not_known'
                customer['location'] = {'name': 'not_known'}

            elif type_of_sale == "WHOLESALE":
                customer['name'] = 'unknown'
                customer['phone'] = '0711111111'
                # customer['location'] = 'not_known'
                customer['location'] = {'name': 'not_known'}

        formdata['customer'] = customer
        formdata['sales_type'] = myDict['sales_type']
        formdata['is_fully_paid'] = myDict['is_fully_paid']
        formdata['partial_payment_amount'] = myDict['partial_payment_amount']
        formdata['exchanged_with_local'] = myDict['exchanged_with_local']
        formdata['debt_amount'] = myDict['debt_amount']
        formdata['repayment_date'] = myDict.get('repayment_date', None)
        formdata['total_amount'] = myDict['total_amount']
        # formdata['mpesa_code'] = myDict['mpesa_code']
        # mpesa_codes = myDict.get('mpesa_code', [])

        # Ensure `mpesa_code` is stored as JSON, not a string
        formdata['mpesa_code'] = myDict.get('mpesa_code', [])

        # Ensure numeric values for `cashAmount` and `mpesaAmount`
        formdata['cashAmount'] = int(myDict.get('cashAmount', 0))
        formdata['mpesaAmount'] = int(myDict.get('mpesaAmount', 0))

        # if isinstance(mpesa_codes, list):
        #     formdata['mpesa_code'] = ",".join(mpesa_codes)  # Convert to comma-separated string
        # else:
        #     formdata['mpesa_code'] = mpesa_codes  # Store as a single string
        # formdata['cash'] = myDict['cash']
        
        formdata['sales_person'] = request.user.id
        formdata['sales_team'] = sales_team
        
        cc = formdata['customer']
        types_of_operation = cc.get('sales')

        formdata['sales_choice'] = types_of_operation
        # Assign sales team
        try:
            employee = Employees.objects.get(user_id=user_id)
            sales_team = employee.sales_team.id
            formdata['sales_agents'] = sales_team
        except Employees.DoesNotExist:
            sales_team = None

        # Process each product
        products = myDict.get('products', [])
        if not products:
            return Response({'error': 'No products provided'}, status=status.HTTP_400_BAD_REQUEST)

        for i, product_data in enumerate(products):
            product_id = product_data.get('id')
            assigned_quantity = int(product_data.get('quantity', 0))

            try:
                assigned_product = AssignedCylinders.objects.get(id=product_id)
            except AssignedCylinders.DoesNotExist:
                return Response({'error': f'Product with ID {product_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if there's enough quantity for the sale
            # print('assigned_quantity', type(assigned_quantity))
            if assigned_product.filled < assigned_quantity:
                
                return Response(
                    {'error': f'Not enough stock for the product. Ask admin for a restock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct the assigned quantity
            assigned_product.filled -= assigned_quantity
         

            if formdata['sales_type'] == "REFILL" and types_of_operation == "WHOLESALE":
                assigned_product.wholesale_refilled += assigned_quantity
                assigned_product.empties += assigned_quantity

            elif formdata['sales_type'] == "COMPLETESALE" and types_of_operation == "WHOLESALE":
                assigned_product.wholesale_sold += assigned_quantity

            elif formdata['sales_type'] == "REFILL" and types_of_operation == "RETAIL":
                assigned_product.retail_refilled += assigned_quantity
                assigned_product.empties += assigned_quantity
                
            elif formdata['sales_type'] == "COMPLETESALE" and types_of_operation == "RETAIL":
                assigned_product.retail_sold += assigned_quantity
                
            assigned_product.save()

            # Create the sales record
            formdata['product'] = product_id
            formdata['quantity'] = assigned_quantity
            serializer = RecordSalesSerializer(data=formdata, context={'request': request})
            if serializer.is_valid():
                sale = serializer.save()
                
                creator = CustomUser.objects.get(id=request.user.id)  
                if not formdata['is_fully_paid'] and i == 0:
                    debt = Dbts.objects.create(
                        creator = creator,
                        sales_tab=sale,
                        customer=sale.customer,
                        amount=formdata['debt_amount'],
                        expected_date_to_repay=formdata['repayment_date']
                    )
                    debt.save()
            else:
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response({'message': 'Sales recorded successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_others_products_sales(request):
    if request.method == 'POST':
        
        user_id = request.user
        custom_user_id = user_id.id
        

        # Get the user's sales team
        try:
            employee = Employees.objects.get(user__id=user_id.id)
            sales_team = employee.sales_team.id
        except Employees.DoesNotExist:
            sales_team = None

        formdata = {}
        user_id = request.user.id
        myDict = request.data

        # Customer and Sale Info
        

        customer = myDict.get('customer', {})
        type_of_sale = customer.get('sales', '')
        

        # Assign default customer details if not provided
        name = customer.get('name', '')
        phone = customer.get('phone', None)
        location = customer.get('location', {}).get('name', '')

        if not name or not phone or not location:
            if type_of_sale == "RETAIL":
                customer['name'] = 'no_name'
                customer['phone'] = '0700000000'
                customer['location'] = {'name': 'not_known'}

            elif type_of_sale == "WHOLESALE":
                customer['name'] = 'unknown'
                customer['phone'] = '0711111111'
                customer['location'] = {'name': 'not_known'}

        formdata['customer'] = customer
        # formdata['sales_type'] = myDict['sales_type']
        formdata['is_fully_paid'] = myDict['is_fully_paid']
        formdata['partial_payment_amount'] = myDict['partial_payment_amount']
        formdata['debt_amount'] = myDict['debt_amount']
        formdata['repayment_date'] = myDict.get('repayment_date', None)
        formdata['total_amount'] = myDict['total_amount']
        
        formdata['sales_person'] = request.user.id
        formdata['sales_team'] = sales_team
        
        cc = formdata['customer']
        types_of_operation = cc.get('sales')

        # formdata['sales_choice'] = types_of_operation
        # Assign sales team
        try:
            employee = Employees.objects.get(user_id=user_id)
            sales_team = employee.sales_team.id
            formdata['sales_agents'] = sales_team
        except Employees.DoesNotExist:
            sales_team = None

        # Process each product
        products = myDict.get('products', [])
        if not products:
            return Response({'error': 'No products provided'}, status=status.HTTP_400_BAD_REQUEST)

        for i, product_data in enumerate(products):
            product_id = product_data.get('id')
            assigned_quantity = product_data.get('quantity', 0)

            try:
                assigned_product = AssignedOtherProducts.objects.get(id=product_id)
            except AssignedOtherProducts.DoesNotExist:
                return Response({'error': f'Product with ID {product_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if there's enough quantity for the sale
            if assigned_product.assigned_quantity < assigned_quantity:
                return Response(
                    {'error': f'Not enough stock for the product. Ask admin for a restock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct the assigned quantity
            assigned_product.assigned_quantity -= assigned_quantity
         

            if types_of_operation == "WHOLESALE":
                assigned_product.wholesale_sold += assigned_quantity
                
          
            elif types_of_operation == "RETAIL":
                assigned_product.retail_sold += assigned_quantity
                
            assigned_product.save()

            # Create the sales record
            formdata['product'] = product_id
            formdata['quantity'] = assigned_quantity
            serializer = RecordOtherProductsSalesSerializer(data=formdata, context={'request': request})
            if serializer.is_valid():
                sale = serializer.save()
                
                creator = CustomUser.objects.get(id=request.user.id)  
                if not formdata['is_fully_paid'] and i == 0:
                    
                    debt = OtherProductsDbts.objects.create(
                        creator = creator,
                        sales_tab=sale,
                        customer=sale.customer,
                        amount=formdata['debt_amount'],
                        expected_date_to_repay=formdata['repayment_date']
                    )
                    debt.save()
            else:
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response({'message': 'Sales recorded successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminMakeSales(APIView):
    def post(self, request):
        print(request.data)

        
    
@api_view(['GET'])
def all_employees(request):
    employees = Employees.objects.all()
    serialize = EmployeesSerializer(employees, context={'request': request}, many=True)
    
    return Response(serialize.data)


        
    
@api_view(['GET'])
def single_employees(request, pk):
    employees = Employees.objects.get(pk = pk)
    serialize = EmployeesSerializer(employees, context={'request': request})
    
    return Response(serialize.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignedProduct(request):
    # Get the logged-in user
    user = request.user

    # Fetch all employee records for the logged-in user
    employee_records = Employees.objects.filter(user=user)

    if not employee_records.exists():
        return Response({"error": "No employee record found for the user."}, status=404)

    # Get all sales teams the employee belongs to
    sales_teams = SalesTeam.objects.filter(employees__in=employee_records).distinct()

    # Filter assigned cylinders by the sales team(s)
    productAssigned = AssignedCylinders.objects.filter(sales_team__in=sales_teams, transaction_complete=False)

    # Serialize the data
    serialize = AssignedCylinderSerializerrr(productAssigned, many=True)
    
    return Response(serialize.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignedOtherProduct(request):
    # Get the logged-in user
    user = request.user

    # Fetch all employee records for the logged-in user
    employee_records = Employees.objects.filter(user=user)

    if not employee_records.exists():
        return Response({"error": "No employee record found for the user."}, status=404)

    # Get all sales teams the employee belongs to
    sales_teams = SalesTeam.objects.filter(employees__in=employee_records).distinct()

    # Filter assigned cylinders by the sales team(s)
    productAssigned = AssignedOtherProducts.objects.filter(sales_team__in=sales_teams)

    # Serialize the data
    serialize = AssignedOtherProductSerializer(productAssigned, many=True)
    
    return Response(serialize.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addassignedProductSpoiled(request):
    
    try:
        # Extract data from request
        product_id = request.data.get('id')
        spoiled_qty = request.data.get('spoiled')

        if not product_id or spoiled_qty is None:
            return Response(
                {'error': 'Product ID and spoiled quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the assigned product
        try:
            assigned_product = AssignedCylinders.objects.get(id=product_id)
        except AssignedCylinders.DoesNotExist:
            return Response(
                {'error': f'Assigned product with ID {product_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate the spoiled quantity
        if spoiled_qty < 0:
            return Response(
                {'error': 'Spoiled quantity cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the spoiled quantity
        assigned_product.spoiled += spoiled_qty
        assigned_product.filled -= spoiled_qty
        assigned_product.save()

        return Response(
            {
                'message': 'Spoiled cylinders updated successfully',
                'id': assigned_product.id,
                'spoiled': assigned_product.spoiled,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'An unexpected error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateassignedProductSpoiled(request):
    
    try:
        # Extract data from request
        product_id = request.data.get('id')
        spoiled_qty = request.data.get('spoiled')

        if not product_id or spoiled_qty is None:
            return Response(
                {'error': 'Product ID and spoiled quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the assigned product
        try:
            assigned_product = AssignedCylinders.objects.get(id=product_id)
        except AssignedCylinders.DoesNotExist:
            return Response(
                {'error': f'Assigned product with ID {product_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate the spoiled quantity
        if spoiled_qty < 0:
            return Response(
                {'error': 'Spoiled quantity cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the spoiled quantity
        if spoiled_qty > assigned_product.spoiled:
            assigned_product.filled -= (spoiled_qty-assigned_product.spoiled)
            assigned_product.spoiled == spoiled_qty
        elif spoiled_qty < assigned_product.spoiled:
            assigned_product.filled += (assigned_product.spoiled - spoiled_qty)
            assigned_product.spoiled == spoiled_qty

        assigned_product.save()

        return Response(
            {
                'message': 'Spoiled cylinders updated successfully',
                'id': assigned_product.id,
                'spoiled': assigned_product.spoiled,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'An unexpected error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sendsms(request):
    if request.method == 'POST':
        selected_group = request.data.get('customer')
        message_text = request.data.get('message')
        for item in selected_group:
            customer = Customers.objects.get(id=item)
            send_to = ["+254" + str(customer.phone)]
            smsSender(send_to , message_text)
        # customer = Customers.objects.get(id=selected_group)
        # Create an instance of the serializer with the request data
        serializer = RecordMessageSerializer(data=request.data)

        # Check if the data is valid
        if serializer.is_valid():
            # Save the data to the database
            serializer.save()
            
            # Return a success response
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If the data is not valid, return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # If the user is not authenticated, return a 401 response
    return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)






@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sendbulksms(request):
    if request.method == 'POST':
        
        selected_group = request.data.get('selected_group')
        selected_location_id = request.data.get('selected_location')
        message_text = request.data.get('message')
        # selected_customer_phone_numbers = []
        if selected_group == 'all':
            try:
                # location = Locations.objects.get(id=selected_location_id)
                
                    # location = get_object_or_404(Locations, id=selected_location_id)
                    # locations = [location]

                customers = Customers.objects.all()
                employees = Employees.objects.all()

                message = Messages(message=message_text)
                message.save()
                
                if selected_location_id == 'all':
                    location = Locations.objects.all()
                    message.location.set(location)
                else:
                    location = Locations.objects.get(id=selected_location_id)
                    customers = Customers.objects.filter(location=location)
                    message.location.set([location])

                message.customer.set(customers)
                message.employees.set(employees)
                selected_customer_phone_numbers = ["+254" + str(customer.phone) for customer in customers]
                selected_employees_phone_numbers = ["+254" + str(employee.phone) for employee in employees]
                all_phones = selected_customer_phone_numbers + selected_employees_phone_numbers
               
                for customer in customers:
                    print('Customer:', customer.name)
                
                smsSender(all_phones , message_text)
                return Response({'message': 'SMS sent to all customers and employees.'}, status=status.HTTP_201_CREATED)
            except Locations.DoesNotExist:
                return Response({'error': 'Invalid location ID.'}, status=status.HTTP_400_BAD_REQUEST)
        elif selected_group == 'wholesale':
            try:
                # Get the specified location using the selected_location_id
                # location = Locations.objects.get(id=selected_location_id)

                # Fetch only wholesale customers
                customers = Customers.objects.filter(sales=Customers.WHOLESALE)
                
                message = Messages(message=message_text)
                message.save()
                
                if selected_location_id == 'all':
                    location = Locations.objects.all()
                    message.location.set(location)
                else:
                    location = Locations.objects.get(id=selected_location_id)
                    # customers = Customers.objects.filter(location=location)
                    customers = Customers.objects.filter(sales=Customers.WHOLESALE, location=location)
                    message.location.set([location])
                    
                selected_customer_phone_numbers = ["+254" + str(customer.phone) for customer in customers]
                message.customer.set(customers)
                # message.location.set([location])
                
                for customer in customers:
                    print('Customer:', customer.name)
               
                smsSender(selected_customer_phone_numbers, message_text)
                return Response({'message': 'SMS sent to wholesale customers.'}, status=status.HTTP_201_CREATED)
            except Locations.DoesNotExist:
                return Response({'error': 'Invalid location ID.'}, status=status.HTTP_400_BAD_REQUEST)
        elif selected_group == 'retail':
            try:
                # location = Locations.objects.get(id=selected_location_id)

                customers = Customers.objects.filter(sales=Customers.RETAIL)
                
                message = Messages(message=message_text)
                message.save()
                
                if selected_location_id == 'all':
                    location = Locations.objects.all()
                    message.location.set(location)
                else:
                    location = Locations.objects.get(id=selected_location_id)
                    # customers = Customers.objects.filter(location=location)
                    customers = Customers.objects.filter(sales=Customers.RETAIL, location=location)
                    message.location.set([location])
                    
                # selected_customer_phone_numbers = [customer.phone for customer in customers]
                selected_customer_phone_numbers = ["+254" + str(customer.phone) for customer in customers]
                message.customer.set(customers)
                # message.location.set([location])
               
               
                smsSender(selected_customer_phone_numbers, message_text)
                return Response({'message': 'SMS sent to Retail customers.'}, status=status.HTTP_201_CREATED)
            except Locations.DoesNotExist:
                return Response({'error': 'Invalid location ID.'}, status=status.HTTP_400_BAD_REQUEST)
        elif selected_group == 'employees':
            try:
                # location = Locations.objects.get(id=selected_location_id)

                employees = Employees.objects.all()
                
                message = Messages(message=message_text)
                message.save()
                
                
                message.employees.set(employees)
                selected_employee_phone_numbers = ["+254" + str(employees.phone) for employees in employees]
               
               
                smsSender(selected_customer_phone_numbers, message_text)
                return Response({'message': 'SMS sent to wholesale customers.'}, status=status.HTTP_201_CREATED)
            except Locations.DoesNotExist:
                return Response({'error': 'Invalid location ID.'}, status=status.HTTP_400_BAD_REQUEST)
        elif selected_group == 'debtors':
            try:
        # Get customers with debts from the Dbts table
                debtors = Dbts.objects.all()

                message = Messages(message=message_text)
                message.save()
                
                if selected_location_id == 'all':
                    location = Locations.objects.all()
                    message.location.set(location)
                else:
                    location = Locations.objects.get(id=selected_location_id)
                    customers = Customers.objects.filter(location=location)
                    message.location.set([location])
            # Extract customers associated with the debts
                customers_with_debts = [debtor.customer for debtor in debtors]
                
                selected_customer_with_debt_phone_numbers = ["+254" + str(customers_with_debts.phone) for customers_with_debts in customers_with_debts]
                print('Customers with debts are this ones ', selected_customer_with_debt_phone_numbers)
                message.customer.set(customers_with_debts)
                
                
                smsSender(selected_customer_with_debt_phone_numbers, message_text)
                return Response({'message': 'SMS sent to debtors.'}, status=status.HTTP_201_CREATED)
            except Dbts.DoesNotExist:
                return Response({'error': 'No customers with debts found.'}, status=status.HTTP_400_BAD_REQUEST)
                # print('Hello Debtors')
                # return Response({'message': 'SMS sent to wholesale customers.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid selected_group value.'}, status=status.HTTP_400_BAD_REQUEST)
  
  
#   081476f218d28a1a680a78086d13efa2d3e94044433f2c743dbc15db302d57b1

# username = "YOUR_USERNAME"    # use 'sandbox' for development in the test environment
# api_key = "081476f218d28a1a680a78086d13efa2d3e94044433f2c743dbc15db302d57b1"      # use your sandbox app API key for development in the test environment
# africastalking.initialize(username, api_key)


# # Initialize a service e.g. SMS
# sms = africastalking.SMS


# # Use the service synchronously
# response = sms.send("Hello Message!", ["+2547xxxxxx"])
# print(response)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_sales_team(request):
    sales_team = SalesTeam.objects.order_by('-date_created')
    serialize = SalesTeamSerializer(sales_team, many=True)
    return Response(serialize.data)



@api_view(['POST'])
def assign_products(request):
    serializer = AddAssignedCylinder(data=request.data, context={'request': request})
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except serializers.ValidationError as e:
        print('Validation errors:', e.detail)
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_assigned_quantity(request, pk):
    try:
        assigned_cylinder = AssignedCylinders.objects.get(pk=pk)
    except AssignedCylinders.DoesNotExist:
        return Response({"error": "AssignedCylinder not found"}, status=status.HTTP_404_NOT_FOUND)

    # Assuming you send the new quantity in the request data
    new_quantity = int(request.data.get('new_quantity', 0))

    # Increment the assigned_quantity
    assigned_cylinder.assigned_quantity += new_quantity
    assigned_cylinder.save()

    serializer = AssignedCylindersSerializer(assigned_cylinder)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
   
    
@api_view(['GET'])    
def sales_team_management(request):
    sales_team = SalesTeam.objects.order_by("-date_created")
    serialize = all_sales_teamSerializer(sales_team, many=True, context = {"request": request})
    
    return Response(serialize.data)



@api_view(['POST'])
def createteam(request):
    
    serializer = CreateSalesTeamSerializer(data=request.data, context={'request': request})
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except serializers.ValidationError as e:
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
    
    

    
@api_view(['GET'])
def Stores(request):
    store = CylinderType.objects.order_by("-date_added")
    serializer = CylinderTypeSerializer(store, many=True)

    return Response(serializer.data)


class OtherProductsViews(APIView):
    def get(self, request):
        products = OtherProducts.objects.order_by('-date_of_operation')
        serialize = OtherProductsSerializer(products, many=True)

        return Response(serialize.data)


    def post(self, request):
        
        serializer = CreateOtherProductsSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            # print('error ', e.default_detail)
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
    



class RefillOperations(APIView):
    def post(self, request):
        # Extract data from the request
        pk = request.data.get('id')
        empties_to_refill = request.data.get('empties')

        if pk is None or empties_to_refill is None:
            return Response({'error': 'ID and empties are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            empties_to_refill = int(empties_to_refill)
        except ValueError:
            return Response({'error': 'Empties must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the CylinderStore instance or return a 404
        store = get_object_or_404(CylinderStore, pk=pk)

        # Check if there are enough empties to refill
        if empties_to_refill > store.empties:
            return Response(
                {'error': 'Not enough empties available to refill'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the fields
        store.empties -= empties_to_refill
        store.filled += empties_to_refill
        store.save()

        # Return a success response with updated data
        return Response(
            {
                'message': 'Refill operation successful',
                'updated_store': {
                    'id': store.id,
                    'empties': store.empties,
                    'filled': store.filled,
                    'spoiled': store.spoiled,
                    'total_cylinders': store.total_cylinders,
                }
            },
            status=status.HTTP_200_OK
        )



class AddNewCylinder(APIView):
    def post(self, request):
        
        serializer = CylinderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        data = serializer.validated_data
        gas_type_name = data['gas_type']
        weight_value = data['weight']
        min_wholesale_selling_price = data['min_wholesale_selling_price']
        min_wholesale_refil_price = data['min_wholesale_refil_price']
        min_retail_selling_price = data['min_retail_selling_price']
        min_retail_refil_price = data['min_retail_refil_price']
        max_wholesale_selling_price = data['max_wholesale_selling_price']
        max_wholesale_refil_price = data['max_wholesale_refil_price']
        max_retail_selling_price = data['max_retail_selling_price']
        max_retail_refil_price = data['max_retail_refil_price']
        filled = data['filled']
        empties = data['empties']
        spoiled = data['spoiled']

        # Check if the gas type exists
        # gas_type, created_gas_type = CylinderType.objects.filter(name=gas_type_name).first()
        gas_type, created_gas_type = CylinderType.objects.get_or_create(name=gas_type_name) 
       
        weight, created_weight = CylinderWeight.objects.get_or_create(weight=weight_value)
        # if not weight:
       
        cylinder = Cylinder.objects.filter(gas_type=gas_type, weight=weight).first()

        if not cylinder:
            # Create the new cylinder if it doesn't exist
            cylinder = Cylinder.objects.create(
                gas_type=gas_type,
                weight=weight,
                min_wholesale_selling_price=min_wholesale_selling_price,
                min_wholesale_refil_price=min_wholesale_refil_price,
                min_retail_selling_price=min_retail_selling_price,
                min_retail_refil_price=min_retail_refil_price,
                max_wholesale_selling_price=max_wholesale_selling_price,
                max_wholesale_refil_price=max_wholesale_refil_price,
                max_retail_selling_price=max_retail_selling_price,
                max_retail_refil_price=max_retail_refil_price,
            )

        # Add the cylinder to CylinderStore
        store = CylinderStore.objects.create(
            cylinder=cylinder,
            filled=filled,
            empties=empties,
            total_cylinders=filled + empties,
            spoiled = spoiled,
            dates=datetime.now(),
        )

        return Response({
            'message': 'Cylinder created and added to store successfully',
            'cylinder': {
                'id': cylinder.id,
                'gas_type': cylinder.gas_type.name,
                'weight': cylinder.weight.weight,
                'min_wholesale_selling_price': cylinder.min_wholesale_selling_price,
                'min_wholesale_refil_price': cylinder.min_wholesale_refil_price,
                'min_retail_selling_price': cylinder.min_retail_selling_price,
                'min_retail_refil_price': cylinder.min_retail_refil_price,
                'max_wholesale_selling_price': cylinder.max_wholesale_selling_price,
                'max_wholesale_refil_price': cylinder.max_wholesale_refil_price,
                'max_retail_selling_price': cylinder.max_retail_selling_price,
                'max_retail_refil_price': cylinder.max_retail_refil_price,
            },
            'store': {
                'id': store.id,
                'filled': store.filled,
                'empties': store.empties,
                'total_cylinders': store.total_cylinders,
            }
        }, status=status.HTTP_201_CREATED)


class CylinderOperations(APIView):
    def put(self, request, pk):
        
        # pk = request.data.get("cylinderId")
        # updated_data = request.data.get("updatedName")
        try:
            cylinder = CylinderType.objects.get(pk=pk)
        except CylinderType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serialize = CylinderTypeUpdateSerializer(cylinder, data = request.data)
      
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AnotherCylinder(APIView):
    def post(self, request, pk):
        
        # Get the gas_type (CylinderType) by ID
        try:
            cylinder_type = CylinderType.objects.get(pk=pk)
        except CylinderType.DoesNotExist:
            return Response({'error': 'Gas type not found'}, status=status.HTTP_404_NOT_FOUND)

        # Extract weight from the request data
        weight_data = request.data.get('weight')
        if not weight_data:
            return Response({'error': 'Weight is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a weight already exists or create one
        weight_instance, _ = CylinderWeight.objects.get_or_create(weight=int(weight_data))  # Convert weight to integer
        
        # Convert all prices and other numeric fields to integers
        try:
            min_wholesale_selling_price = int(request.data.get('min_wholesale_selling_price', 0))
            min_wholesale_refil_price = int(request.data.get('min_wholesale_refill_price', 0))
            min_retail_selling_price = int(request.data.get('min_retail_selling_price', 0))
            min_retail_refil_price = int(request.data.get('min_retail_refill_price', 0))

            max_wholesale_selling_price = int(request.data.get('max_wholesale_selling_price', 0))
            max_wholesale_refil_price = int(request.data.get('max_wholesale_refill_price', 0))
            max_retail_selling_price = int(request.data.get('max_retail_selling_price', 0))
            max_retail_refil_price = int(request.data.get('max_retail_refill_price', 0))

            empties = int(request.data.get('empties', 0))
            filled = int(request.data.get('filled', 0))
            spoiled = int(request.data.get('spoiled', 0))
        except ValueError:
            return Response({'error': 'All numeric fields must contain valid integers'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new cylinder
        cylinder = Cylinder.objects.create(
            gas_type=cylinder_type,
            weight=weight_instance,
            min_wholesale_selling_price=min_wholesale_selling_price,
            min_wholesale_refil_price=min_wholesale_refil_price,
            min_retail_selling_price=min_retail_selling_price,
            min_retail_refil_price=min_retail_refil_price,
            max_wholesale_selling_price=max_wholesale_selling_price,
            max_wholesale_refil_price=max_wholesale_refil_price,
            max_retail_selling_price=max_retail_selling_price,
            max_retail_refil_price=max_retail_refil_price,
        )

        # Optionally, save cylinder store data if required
        cylinder_store = CylinderStore.objects.create(
            cylinder=cylinder,
            empties=empties,
            filled=filled,
            spoiled=spoiled,
            total_cylinders=empties + filled + spoiled,
            dates=datetime.now(),
        )

        # Return success response
        return Response(
            {
                'message': "New cylinder and store data created successfully.",
                'cylinder_id': cylinder.id,
                'gas_type': cylinder.gas_type.name,
                'weight': cylinder.weight.weight,
                'min_wholesale_selling_price': cylinder.min_wholesale_selling_price,
                'min_wholesale_refil_price': cylinder.min_wholesale_refil_price,
                'min_retail_selling_price': cylinder.min_retail_selling_price,
                'min_retail_refil_price': cylinder.min_retail_refil_price,
                'max_wholesale_selling_price': cylinder.max_wholesale_selling_price,
                'max_wholesale_refil_price': cylinder.max_wholesale_refil_price,
                'max_retail_selling_price': cylinder.max_retail_selling_price,
                'max_retail_refil_price': cylinder.max_retail_refil_price,
                'empties': cylinder_store.empties,
                'filled': cylinder_store.filled,
                'spoiled': cylinder_store.spoiled,
                'total_cylinders': cylinder_store.total_cylinders,
            },
            status=status.HTTP_201_CREATED
        )

        

    def delete(self, request, pk):
        
        try:
            cylinder = CylinderType.objects.get(pk=pk)
        except CylinderType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        cylinder.delete()
        return Response('Deleted')
    



class AssignCylinderView(APIView):
    def post(self, request):
        serializer = AssignedCylinderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add the logged-in user as the creator
        serializer.save(creator=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class BulkAssignCylinderView(APIView):
    def post(self, request):
        # Ensure the request data is a list
        if not isinstance(request.data, list):
            return Response({"error": "Expected a list of assignments"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BulkAssignedCylinderSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # Process each assignment
        assignments = []
        for item in serializer.validated_data:
            sales_team = item['sales_team']
            cylinder_store = item['cylinder']
            new_quantity = item['assigned_quantity']

            # Check if an assignment already exists for this sales team and cylinder
            existing_assignment = AssignedCylinders.objects.filter(
                sales_team=sales_team,
                cylinder=cylinder_store
            ).exclude(transaction_complete=True).first()

            if existing_assignment:
                # Update the assigned quantity for incomplete transactions
                existing_assignment.assigned_quantity += new_quantity
                existing_assignment.filled += new_quantity
                existing_assignment.save()
            else:
                # Create a new assignment if no incomplete transaction exists
                existing_assignment = AssignedCylinders.objects.create(
                    creator=request.user,
                    sales_team=sales_team,
                    cylinder=cylinder_store,
                    assigned_quantity=new_quantity,
                    filled=new_quantity
                )

            # Reduce the filled quantity in CylinderStore
            if cylinder_store.filled >= new_quantity:
                cylinder_store.filled -= new_quantity
                cylinder_store.save()
            else:
                raise serializers.ValidationError(
                    f"Not enough filled cylinders available. Current filled: {cylinder_store.filled}"
                )

            assignments.append(existing_assignment)
            AssignedCylindersRecipt.objects.create(
                sales_team=sales_team,
                cylinder=cylinder_store,
                assigned_quantity=new_quantity
            )


        # Serialize and return the created or updated assignments
        response_data = [
            {
                "id": assignment.id,
                "sales_team": assignment.sales_team.id,
                "cylinder": assignment.cylinder.id,
                "assigned_quantity": assignment.assigned_quantity,
                "date_assigned": assignment.date_assigned,
            }
            for assignment in assignments
        ]

        return Response(response_data, status=status.HTTP_201_CREATED)


class AssignedCylindersPrintableView(APIView):
    def get(self, request):
        # Optionally filter by sales team if provided
        sales_team_id = request.query_params.get('sales_team')
        if sales_team_id:
            assigned_cylinders = AssignedCylindersRecipt.objects.filter(sales_team_id=sales_team_id, print_complete=False)
        else:
            assigned_cylinders = AssignedCylindersRecipt.objects.all()

        serializer = AssignedCylinderReceiptSerializer(assigned_cylinders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ReturnCylindersPrintableView(APIView):
    def get(self, request):
        # Optionally filter by sales team if provided
        sales_team_id = request.query_params.get('sales_team')
        if sales_team_id:
            return_cylinders = ReturnClylindersReciept.objects.filter(sales_team_id=sales_team_id, print_complete=False)
        # else:
        #     return_cylinders = ReturnClylindersReciept.objects.all()
        
        serializer = ReturnCylinderReceiptSerializer(return_cylinders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AssignedCylindersListView(APIView):
    def get(self, request):
        # Optionally filter by sales team if provided
        sales_team_id = request.query_params.get('sales_team')
        if sales_team_id:
            assigned_cylinders = AssignedCylinders.objects.filter(sales_team_id=sales_team_id, transaction_complete=False)
            
        else:
            assigned_cylinders = AssignedCylinders.objects.all()

        serializer = AssignedCylinderSerializerrr(assigned_cylinders, many=True)
        # print('assigned ', serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AssingnedCylindersLost(APIView):
    def post(self, request):
        try:
            # Extract sales team and cylinder loss details
            sales_team_id = request.data.get('sales_team_id')
            losses = request.data.get('losses', [])

            if not sales_team_id or not losses:
                return Response({"error": "Sales team ID and losses are required."}, status=status.HTTP_400_BAD_REQUEST)

            for loss in losses:
                employee_id = loss.get('employee_id')
                cylinder_id = loss.get('cylinder_id')
                filled_lost = loss.get('filled_lost', 0)
                empties_lost = loss.get('empties_lost', 0)

                # Update assigned cylinder record
                assigned_cylinder = AssignedCylinders.objects.filter(
                    sales_team_id=sales_team_id,
                    cylinder_id=cylinder_id,
                    transaction_complete=False
                ).first()

                if assigned_cylinder:
                    assigned_cylinder.filled_lost += filled_lost
                    assigned_cylinder.empties_lost += empties_lost
                    assigned_cylinder.save()


                    CylinderLost.objects.create(
                        employee_id=employee_id,
                        cylinder=assigned_cylinder,
                        number_of_filled_cylinder=filled_lost,
                        number_of_empty_cylinder=empties_lost
                    )

                
            # Serialize and return the updated data
            updated_cylinders = AssignedCylinders.objects.filter(sales_team_id=sales_team_id, transaction_complete=False)
            serializer = AssignedCylinderSerializerrr(updated_cylinders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssingnedCylindersLessPay(APIView):
    def post(self, request):
       
        try:
            # Extract sales team and cylinder loss details
            sales_team_id = request.data.get('sales_team_id')
            lesses = request.data.get('lesses', [])

            if not sales_team_id or not lesses:
                return Response({"error": "Sales team ID and lesses are required."}, status=status.HTTP_400_BAD_REQUEST)

            for less in lesses:
                employee_id = less.get('employee_id')
                cylinder_id = less.get('cylinder_id')
                less = less.get('less_pay', 0)
                

                # Update assigned cylinder record
                assigned_cylinder = AssignedCylinders.objects.filter(
                    sales_team_id=sales_team_id,
                    cylinder_id=cylinder_id,
                    transaction_complete=False
                ).first()

                if assigned_cylinder:
                    assigned_cylinder.less_pay += less
                    # assigned_cylinder.empties += less
                    assigned_cylinder.save()


                    CylinderLessPay.objects.create(
                        employee_id=employee_id,
                        cylinder=assigned_cylinder,
                        cylinders_less_pay = less,
                    )

                
            # Serialize and return the updated data
            updated_cylinders = AssignedCylinders.objects.filter(sales_team_id=sales_team_id, transaction_complete=False)
            serializer = AssignedCylinderSerializerrr(updated_cylinders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnAssignedCylindersView(APIView):
    def post(self, request):
        serializer = ReturnCylindersSerializer(data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_cylinders = []

        for assignment in serializer.validated_data:
            try:
                assigned_cylinder = AssignedCylinders.objects.get(id=assignment['id'])
                
                if not assigned_cylinder.transaction_complete:
                    # Return cylinders and capture returned values
                    filled, empties, spoiled, filled_lost, empties_lost, less_pay = assigned_cylinder.return_cylinders()
                    updated_cylinders.append(assigned_cylinder)

                    
                    # Create a return receipt for the completed transaction
                    ReturnClylindersReciept.objects.create(
                        sales_team=assigned_cylinder.sales_team,
                        cylinder=assigned_cylinder.cylinder,
                        filled=filled,
                        empties=empties,
                        filled_lost=filled_lost,
                        empties_lost=empties_lost,
                        less_pay = less_pay,
                        spoiled=spoiled,
                    )

            except AssignedCylinders.DoesNotExist:
                return Response({"error": f"AssignedCylinder with ID {assignment['id']} does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        # Serialize the updated cylinders
        response_serializer = ReturnCylindersSerializer(updated_cylinders, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ReturnAllAssignedCylindersView(APIView):
    def post(self, request):
        serializer = ReturnCylindersSerializer(data=request.data, many=True, partial=True)
        
        serializer.is_valid(raise_exception=True)

        updated_cylinders = []

        for assignment in serializer.validated_data:
          
            try:
                assigned_cylinder = AssignedCylinders.objects.get(id=assignment['id'])
                # return_filled = assignment.get('return_filled', False) 
                if not assigned_cylinder.transaction_complete:
                    # assigned_cylinder.return_all_cylinders()
                    filled, empties, spoiled, filled_lost, empties_lost, less_pay  = assigned_cylinder.return_all_cylinders()
                    updated_cylinders.append(assigned_cylinder)
                   
                    # Create a return receipt for the completed transaction
                    ReturnClylindersReciept.objects.create(
                        sales_team=assigned_cylinder.sales_team,
                        cylinder=assigned_cylinder.cylinder,
                        filled = filled-filled_lost-less_pay,
                        empties=empties+less_pay-empties_lost,
                        filled_lost=filled_lost,
                        empties_lost=empties_lost,
                        spoiled=spoiled,
                        less_pay = less_pay
                    )

            except AssignedCylinders.DoesNotExist:
                return Response({"error": f"AssignedCylinder with ID {assignment['id']} does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        # Serialize the updated cylinders
        response_serializer = ReturnCylindersSerializer(updated_cylinders, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

class DefaultedCylinders(APIView):
    def get(self, request, employee_id):
        # employee = request.query_params.get('employee_id')
        
        # if employee:
        lost_cylinders = CylinderLost.objects.filter(employee = employee_id,  resolved = False)

        serialize = LostCylindersSerializer(lost_cylinders, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)
    
class DefaultedCylindersLessPay(APIView):
    def get(self, request, employee_id):
        # employee = request.query_params.get('employee_id')
        
        # if employee:
        lost_cylinders = CylinderLessPay.objects.filter(employee = employee_id, resolved = False)

        serialize = LessPayCylindersSerializer(lost_cylinders, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)

class PaymentsProcess(APIView):
    def post(self, request, pk):
        return Response('Payment process Complete.')
    

@api_view(['PATCH'])
def resolve_cylinder_lost(request, pk):
    try:
        # Retrieve the cylinder loss instance by primary key
        cylinder_lost = CylinderLost.objects.get(pk=pk)
    except CylinderLost.DoesNotExist:
        return Response({"error": "CylinderLost not found."}, status=status.HTTP_404_NOT_FOUND)

    # Directly update and save the resolved status
    cylinder_lost.resolved = True
    cylinder_lost.save()

    return Response({"message": f"Cylinder loss {pk} resolved successfully."})
  


@api_view(['PATCH'])
def return_cylinder_lost(request, pk):
    try:
        # Retrieve the cylinder loss instance by primary key
        cylinder_lost = CylinderLost.objects.get(pk=pk)
        cylinder_store = cylinder_lost.cylinder.cylinder
    
    except CylinderLost.DoesNotExist:
        return Response({"error": "CylinderLost not found."}, status=status.HTTP_404_NOT_FOUND)

    if cylinder_lost.number_of_empty_cylinder >= 1:
        cylinder_store.empties += cylinder_lost.number_of_empty_cylinder
        cylinder_lost.resolved = True
        cylinder_lost.save()
        cylinder_store.save()
        return Response({'message': 'Cylinder returned.'})
    elif cylinder_lost.number_of_filled_cylinder >= 1:
        cylinder_store.filled += cylinder_lost.number_of_filled_cylinder
        cylinder_lost.resolved = True
        cylinder_lost.save()
        cylinder_store.save()
        return Response({'message': 'Cylinder returned.'})
    # # Directly update and save the resolved status
    # cylinder_lost.resolved = True
    # cylinder_lost.save()

    # return Response({"message": f"Cylinder loss {pk} resolved successfully."})
  


@api_view(['PATCH'])
def resolve_cylinder_lessPay(request, pk):
    try:
        # Retrieve the cylinder loss instance by primary key
        cylinder_less_pay = CylinderLessPay.objects.get(pk=pk)
    except CylinderLessPay.DoesNotExist:
        return Response({"error": "CylinderLess pay not found."}, status=status.HTTP_404_NOT_FOUND)

    # Directly update and save the resolved status
    cylinder_less_pay.resolved = True
    cylinder_less_pay.save()

    return Response({"message": f"Cylinder less pay {pk} resolved successfully."})
  

class MarkPrintCompleteView(APIView):
    def post(self, request):
        sales_team_id = request.data.get("sales_team_id")

        # Ensure the sales_team_id is provided
        if not sales_team_id:
            return Response({"error": "Sales team ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark print_complete as True for the matching records
        # ReturnClylindersReciept.objects.filter(sales_team_id=sales_team_id, print_complete=False).update(print_complete=True)
        AssignedCylindersRecipt.objects.filter(sales_team_id=sales_team_id, print_complete=False).update(print_complete=True)

        return Response({"message": "Print status successfully updated."}, status=status.HTTP_200_OK)

class MarkPrintOthersCompleteView(APIView):
    def post(self, request):
        sales_team_id = request.data.get("sales_team_id")

        # Ensure the sales_team_id is provided
        if not sales_team_id:
            return Response({"error": "Sales team ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark print_complete as True for the matching records
        # ReturnClylindersReciept.objects.filter(sales_team_id=sales_team_id, print_complete=False).update(print_complete=True)
        AssignedOtherProductRecipt.objects.filter(sales_team_id=sales_team_id, print_complete=False).update(print_complete=True)

        return Response({"message": "Print status successfully updated."}, status=status.HTTP_200_OK)

class MarkPrintReturnCompleteView(APIView):
    def post(self, request):
        sales_team_id = request.data.get("sales_team_id")

        # Ensure the sales_team_id is provided
        if not sales_team_id:
            return Response({"error": "Sales team ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark print_complete as True for the matching records
        ReturnClylindersReciept.objects.filter(sales_team_id=sales_team_id, print_complete=False).update(print_complete=True)
        # AssignedCylindersRecipt.objects.filter(sales_team_id=sales_team_id, print_complete=False).update(print_complete=True)

        return Response({"message": "Print status successfully updated."}, status=status.HTTP_200_OK)




class BulkAssignOtherProductsView(APIView):
    def post(self, request):
        
        if not isinstance(request.data, list):
            return Response({"error": "Expected a list of products"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BulkAssignedOtherProductsSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # Process each assignment
        assignments = []
        for item in serializer.validated_data:
            sales_team = item['sales_team']
            product_store = item['product']
            new_quantity = item['assigned_quantity']

            # Check if an assignment already exists for this sales team and cylinder
            existing_assignment = AssignedOtherProducts.objects.filter(
                sales_team = sales_team,
                product = product_store
            ).exclude(transaction_complete=True).first()

            if existing_assignment:
                # Update the assigned quantity for incomplete transactions
                existing_assignment.assigned_quantity += new_quantity
                # existing_assignment.filled += new_quantity
                existing_assignment.save()
            else:
                # Create a new assignment if no incomplete transaction exists
                existing_assignment = AssignedOtherProducts.objects.create(
                    creator=request.user,
                    sales_team=sales_team,
                    product = product_store,
                    assigned_quantity=new_quantity,
                    
                )

            # Reduce the filled quantity in CylinderStore
            if product_store.quantity >= new_quantity:
                product_store.quantity -= new_quantity
                product_store.save()
            else:
                raise serializers.ValidationError(
                    f"Not enough filled product available. Current number is: {product_store.quantity}"
                )

            assignments.append(existing_assignment)
            AssignedOtherProductRecipt.objects.create(
                sales_team=sales_team,
                product = product_store,
                assigned_quantity=new_quantity
            )


        # Serialize and return the created or updated assignments
        response_data = [
            {
                "id": assignment.id,
                "sales_team": assignment.sales_team.id,
                "product": assignment.product.id,
                "assigned_quantity": assignment.assigned_quantity,
                "date_assigned": assignment.date_assigned,
            }
            for assignment in assignments
        ]

        return Response(response_data, status=status.HTTP_201_CREATED)

class OtherProductsRecietPrint(APIView):
    def get(self, request):
        # Optionally filter by sales team if provided
        sales_team_id = request.query_params.get('sales_team')
        if sales_team_id:
            assigned_product = AssignedOtherProductRecipt.objects.filter(sales_team_id=sales_team_id, print_complete=False)
        else:
            assigned_product = AssignedOtherProductRecipt.objects.all()

        serializer = AssignedOtherProductReceiptSerializer(assigned_product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ViewAllSales(APIView):
    def get(self, request):
        all_sales = SalesTab.objects.order_by('-date_sold')

class TeamExpensesOperation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, salesTeam_id):
        expenses = Expenses.objects.filter(sales_team = salesTeam_id, resolved=False).order_by('-date')
        serialize = ExpensesSerializer(expenses, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)
    
class ExpensesOperation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, employee_id):
        expenses = Expenses.objects.filter(employee = employee_id, resolved=False).order_by('-date')
        serialize = ExpensesSerializer(expenses, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)

    def post(self, request, employee_id):
        data = request.data.copy()
        serializer = ExpensesSerializer(data=data, context={"request": request}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('Error is ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # # print('request data ', request.data)
        # return Response('ok')

class CashHandoutOperation(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, employee_id):
        print('request data ', request.data)
        
        # today = date.today()
        sales_team_id = int(request.data.get('sales_team'))
        cash = int(request.data.get('cash_at_hand'))
        cash_default = int(request.data.get('cash_default'))
        date_data = request.data.get('date')

        try:
            existing = CashHandOut.objects.get(sales_team_id=sales_team_id, date=date_data)
            print("✅ Updating existing cash handout entry")

            existing.cash = cash
            existing.cash_default = cash_default
            existing.employee_id = employee_id
            existing.date = date_data
            existing.save()

            serializer = CashHandOutSerializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except CashHandOut.DoesNotExist:
            print("🆕 Creating new cash handout entry")

            data = {
                "employee": employee_id,
                "sales_team": sales_team_id,
                "cash": cash,
                "cash_default": cash_default,
                "date": date_data
            }

            serializer = CashHandOutSerializer(data=data, context={"request": request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print("❌ Serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer = CashHandOutSerializer(data=data, context={"request": request}, partial=True)

        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     print('Error is ', serializer.errors)
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


    def get(self, request):
        cash_handouts = CashHandOut.objects.filter( resolved=False).order_by('-date')
        serialize = CashHandOutSerializer(cash_handouts, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)
    


class MyProfiles(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        profile = Employees.objects.get(user = user)
        serialize = MyProfileSerializer(profile, context={'request': request})

        return Response(serialize.data)
    
    def put(self, request):
        user = request.user
        try:
            profile = Employees.objects.get(user=user)
        except Employees.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MyProfileSerializer(profile, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        user = request.user
        print('Calling here!')

        # Check if the employee profile already exists
        if Employees.objects.filter(user=user).exists():
            return Response({"error": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the request data to associate the profile with the logged-in user
        data = request.data.copy()
        data["user"] = user.id

        # Serialize and create a new employee profile
        serializer = CreateMyProfileSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('Error is ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SalesRecordsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        print('here')
        user = request.user

        # Retrieve the employee and their sales team
        try:
            employee = Employees.objects.get(user=user)
            sales_team = employee.sales_team
            if not sales_team:
                return Response({"error": "User is not assigned to a sales team"}, status=400)
        except Employees.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=404)

        # Filter sales by the sales team
        sales = SalesTab.objects.filter(sales_team=sales_team).order_by('-date_sold')

        # Serialize the sales data
        serializer = SalesRecordSerializer(sales, many=True, context={'request': request})
        return Response(serializer.data, status=200)


class AdminSalesRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve sales records ordered by date sold
            sales = SalesTab.objects.order_by('-date_sold')

            # If no sales are found, return a meaningful response
            if not sales.exists():
                return Response(
                    {'message': 'No sales records found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize sales data
            serializer = SalesRecordSerializer(sales, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            return Response(
                {'error': 'An error occurred while retrieving sales records', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

class AdminVerifySalesRecordsView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, sale_id):
        # print('data requested', request.data)
        sales_type =  request.data
        # print('data requested', sales_type.get('paymentType'))
        

        try:
            sale = SalesTab.objects.get(id=sale_id)
            if sales_type.get('paymentType') == 'mpesa':
                print('sales type is mpesa')
                sale.admin_mpesa_verified = not sale.admin_mpesa_verified
                sale.save()

            if sales_type.get('paymentType') == 'cash':
                print('sales type is cash')
                sale.admin_payment_verified = not sale.admin_payment_verified
                sale.save()
            
            serializer = SalesRecordSerializer(sale)
            print('response data ', serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SalesTab.DoesNotExist:
            return Response({"error": "Sale not found."}, status=status.HTTP_404_NOT_FOUND)




class CheckUserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Check if the user has an employee profile
        employee_profile = Employees.objects.filter(user=user).first()
        has_employee_profile = employee_profile is not None
        is_verified = employee_profile.verified if employee_profile else False
        is_admin = user.is_superuser

        return Response({
            "has_employee_profile": has_employee_profile,
            "is_verified": is_verified,
            "is_admin": is_admin
        })


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_employee_status(request, employee_id):
    
    try:
        # Fetch the employee object
        employee = Employees.objects.get(id=employee_id)
        user = employee.user  # Get the associated CustomUser

        print("Direct User Permissions:", user.user_permissions.all())

        # Check if the user has the correct permission
        print("Has employee permission:", user.has_perm("Users.is_employee"))

        # Verify the permission exists in the database
        permission = Permission.objects.get(codename="is_employee")
        print("Permission Exists:", permission)
        # Fetch the status field
        status_field = request.data.get('status_field')

        # Validate the status field
        if not status_field:
            return Response({"error": "Missing status_field in request"}, status=status.HTTP_400_BAD_REQUEST)

        # Handle "verified" status
        if status_field == "verified":
            content_type = ContentType.objects.get_for_model(CustomUser)
            employee_permission, _ = Permission.objects.get_or_create(
                codename="is_employee",
                defaults={
                    "name": "Can act as an employee",
                    "content_type": content_type,
                },
            )

            if employee.verified:
                # Unverify the employee and remove the "is_employee" permission
                employee.verified = False
                user.user_permissions.remove(employee_permission)
                # user.is_active = False  # Optionally deactivate the user
            else:
                # Verify the employee and add the "is_employee" permission
                employee.verified = True
                user.user_permissions.add(employee_permission)
                user.is_active = True  # Activate the user

                

        # Handle "fire" status
        elif status_field == "fire":
            content_type = ContentType.objects.get_for_model(CustomUser)
            employee_permission, _ = Permission.objects.get_or_create(
                codename="is_employee",
                defaults={
                    "name": "Can act as an employee",
                    "content_type": content_type,
                },
            )

            if employee.fired:
                # Unfire the employee
                employee.fired = False
                employee.verified = True  # Re-verify the employee
                user.user_permissions.add(employee_permission)
                user.is_active = True  # Activate the user
            else:
                # Fire the employee
                employee.fired = True
                employee.verified = False
                user.user_permissions.remove(employee_permission)
                user.is_active = False  # Deactivate the user

        # Invalid status_field
        else:
            return Response({"error": "Invalid status_field value"}, status=status.HTTP_400_BAD_REQUEST)

        # Save both models
        user.save()
        employee.save()

        # Serialize the updated employee data
        serialized_employee = EmployeesSerializer(employee, context={'request': request})
        return Response(
            {"message": f"{status_field} toggled successfully", "employee": serialized_employee.data},
            status=status.HTTP_200_OK
        )

    except Employees.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def transfer_employee(request, employee_id):
    try:
        # Get the employee
        employee = Employees.objects.get(id=employee_id)

        # Get the sales team ID from the request
        sales_team_id = request.data.get('sales_team_id')
        if not sales_team_id:
            return Response({"error": "Sales team ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the target sales team
        try:
            sales_team = SalesTeam.objects.get(id=sales_team_id)
        except SalesTeam.DoesNotExist:
            return Response({"error": "Sales team not found"}, status=status.HTTP_404_NOT_FOUND)

        # Assign the employee to the new sales team
        employee.sales_team = sales_team
        employee.save()

        # Serialize the updated employee data
        serialized_employee = EmployeesSerializer(employee, context={'request': request})
        return Response(
            {"message": "Employee transferred successfully", "employee": serialized_employee.data},
            status=status.HTTP_200_OK
        )
    except Employees.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class DebtOperation(APIView):
    def post(self, request, pk):
        debt = get_object_or_404(Dbts, pk=pk)

        if debt.cleared:  # Optional check if it's already cleared
            return Response(
                {"message": f"Debt {pk} is already cleared."},
                status=status.HTTP_400_BAD_REQUEST
            )

        debt.cleared = True
        debt.save()
        return Response(
            {"message": f"Debt {pk} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    

class EmployeeDetails(APIView):
    def get(self, request, pk, employee_id):
        employee = Employees.objects.get(pk=pk)


        

class EmployeeSalary(APIView):
    def patch(self, request, pk):
        data = request.data
        employee = get_object_or_404(Employees, pk=pk)
        employee.contract_salary = data.get('contract_salary')
        employee.save()

        serialize = EmployeesSerializer(employee)

        return Response(serialize.data, status=status.HTTP_200_OK)
    


class AdvancesOperation(APIView):
    def get(self, request, employeeId):
        advance = Advances.objects.filter(employee=employeeId, resolved=False)
        serialize = AdvancesSerializer(advance, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)
    
    def post(self, request, employeeId):
        serializer = AdvancesSerializer(
            data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class resolve_advances(APIView):  
    def patch(self, request, pk):
        advance = get_object_or_404(Advances, pk=pk)
        
        advance.resolved = True
        advance.save()
        return Response({"message": f"advance resolved successfully."})
      



class CylinderRequested(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, team_id):
        employee = request.user.id
        requests_data = CylinderRequestTransfer.objects.filter(given=False)
        serializer = AllCylinderRequestSerializer(requests_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




class CylinderRequestClear(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, team_id):
        employee = request.user.id
        requests_data = CylinderRequestTransfer.objects.filter(employee=employee, given=False)
        serializer = CylinderRequestSerializer(requests_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class CylinderRequestGet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, team_id):
        employee = request.user.id
        requests_data = CylinderRequestTransfer.objects.get(employee=employee, given=False, cylinder=team_id)
        requests_data.delete()
        return Response({"message": f"Debt deleted successfully."},
            status=status.HTTP_204_NO_CONTENT)
    



class CylinderRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()  # Copy to safely modify
        

        try:
            employee = Employees.objects.get(user=request.user.id)  # Get employee linked to user
        except Employees.DoesNotExist:
            return Response({"error": "No Employee record found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        requesting_team = employee.sales_team
        data['requesting_team'] = requesting_team.id if requesting_team else None  
        data['employee'] = request.user.id  # Assign employee ID from request.user

         # Check if an existing request matches `requesting_team` & `cylinder`
        existing_request = CylinderRequestTransfer.objects.filter(
            employee=request.user.id,
            cylinder_id=data.get('cylinder')
        ).order_by('-date').first()


        if existing_request:
            if not existing_request.given:  # If given == False, just update
                existing_request.quantity = data.get('quantity', existing_request.quantity)
                existing_request.save()
                serializer = CylinderRequestSerializer(existing_request)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # If no existing request or given == True, create a new entry
        serializer = CylinderRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # New record created

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





class CylinderRequestedToMe(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        requests_data = CylinderRequestTransfer.objects.filter(given=False)
        serializer = AllCylinderRequestSerializer(requests_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class ApproveCylinderRequested(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, cylinder_id):
        try:
            cylinder_requested = CylinderRequestTransfer.objects.get(cylinder=cylinder_id)
        except CylinderRequestTransfer.DoesNotExist:
            return Response('Does not exist.', status=status.HTTP_404_NOT_FOUND)
        
        requesting_team = cylinder_requested.requesting_team
        quantity = cylinder_requested.quantity
        
        try:
            assigned_cylinder = AssignedCylinders.objects.get(pk=cylinder_id)
        except AssignedCylinders.DoesNotExist:
            return Response("Cylinder does not exist.", status=status.HTTP_404_NOT_FOUND)
        
        assigned_cylinder.filled -= quantity
        assigned_cylinder.transfered_cylinder += quantity
        assigned_cylinder.save()
        
        assigned_cylinder_store_id = assigned_cylinder.cylinder
        try:
            requesting_team_cylinders = AssignedCylinders.objects.get(sales_team = requesting_team, cylinder = assigned_cylinder_store_id, transaction_complete=False)
           
            requesting_team_cylinders.filled += quantity
            requesting_team_cylinders.save()
            cylinder_requested.given = True
            cylinder_requested.save()
            return Response('ok', status=status.HTTP_201_CREATED)
        except AssignedCylinders.DoesNotExist:
            new_assignment = AssignedCylinders.objects.create(
                    creator=cylinder_requested.employee,
                    sales_team=cylinder_requested.requesting_team,
                    cylinder=assigned_cylinder.cylinder,
                    assigned_quantity=quantity,
                    filled=quantity
                )
            cylinder_requested.given = True
            cylinder_requested.save()
            return Response('ok', status=status.HTTP_201_CREATED)
        # serializer = AllCylinderRequestSerializer(requests_data, many=True)
        return Response('ok', status=status.HTTP_200_OK)
    



class ExpensesOwnerOperation(APIView):
    # ExpensesOwnerOperation
    permission_classes = [IsAuthenticated]
    def post(self, request, expense_id):
        print('request data ', request.data)
        data = request.data.copy()

        
        try:
            expense = Expenses.objects.get(id=expense_id)
        except Expenses.DoesNotExist:
            return Response({"error": "Expense not found."}, status=status.HTTP_404_NOT_FOUND)

        owner = request.data.get('owner')
        if owner == 'Company':
            expense.expense_on_choice = Expenses.COMPANY
            expense.employee = None
            print("Assigned to Company")
            # print('Company is ', data.get('owner'))
        else:
            print('Owner', data.get('Owner'))
            try:
                employee = Employees.objects.get(pk=owner)
                expense.expense_on_choice = Expenses.EMPLOYEE
                expense.employee = employee
                print("Assigned to Employee:", employee)
            except Employees.DoesNotExist:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        # Update the expense with the new data
        expense.save()
        serializer = ExpensesSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # serializer = ExpensesSerializer(expense, data=request.data, partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # else:
        #     print('Error is ', serializer.errors)
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)