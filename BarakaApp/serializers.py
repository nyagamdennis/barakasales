from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from users.serializers import UserSerializer
from collections import defaultdict





class CustomerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = '__all__'


class CylinderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CylinderType
        fields = '__all__'

class CylinderTypeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CylinderType
        fields = '__all__'
        

class CylinderWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = CylinderWeight
        fields = '__all__'


class CylinderSerializer(serializers.ModelSerializer):
    # gas_type = CylinderTypeSerializer()
    # weight = CylinderWeightSerializer()
    
    class Meta:
        model = Cylinder
        fields = '__all__'


class EmployeeSalesTeamView(serializers.ModelSerializer):
    class Meta:
        model = SalesTeam
        fields = '__all__'



class EmployeesSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    sales_team = EmployeeSalesTeamView()
    class Meta:
        model = Employees
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        employees = Employees.objects.create(user=user, **validated_data)
        return employees
    

class AllEmployeesSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employees
        fields = '__all__'

    



class AddCustomerSerializer(serializers.ModelSerializer):
    location = CustomerLocationSerializer(required=False)

    class Meta:
        model = Customers
        fields = '__all__'
        # exclude = ['location']
      
      
    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        phone = validated_data.get('phone')
        
        if Customers.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(f"A customer with phone number {phone} already exists.")

        print('validated ', validated_data)
        if location_data:
            location_name = location_data.get('name')
            
            # location = None
            if location_name:
                # Check if a location with the same name already exists
                location, created = Locations.objects.get_or_create(name=location_name)
                # if not created:
                #     print("not created!")
                #     # Location already existed, so assign it to the customer
                #     validated_data['location'] = location
                
            else:
                # Location data is provided but does not have a 'name' field
                raise serializers.ValidationError("Location 'name' field is required.")

        # Create the customer with the assigned or newly created location
        customer = Customers.objects.create(location=location, **validated_data)
        return customer
    

class AddAssignedCylinder(serializers.ModelSerializer):
    class Meta:
        model = AssignedCylinders
        fields = '__all__'
        
    def create(self, validated_data):
        assigned_quantity = validated_data.get('assigned_quantity')
        cylinder = validated_data.get('cylinder')
        sales_team = validated_data.get('sales_team')
        print('This is the sales team ', sales_team)
        
  
        if assigned_quantity <= 0:
            print("Assigned quantity must be greater than zero.")
            raise serializers.ValidationError("Assigned quantity must be greater than zero.")
        
        # Check if there are enough cylinders available
        if cylinder.quantity < assigned_quantity:
            print("Not enough cylinders available for assignment.")
            raise serializers.ValidationError("Not enough cylinders available for assignment.")
        
        
        # Update the cylinder quantity
        cylinder.quantity -= assigned_quantity
        cylinder.save()

        assigned_cylinder = AssignedCylinders.objects.create( **validated_data)
        return assigned_cylinder
    
   
class RecordSalesSerializer(serializers.ModelSerializer):
    customer = AddCustomerSerializer()

    class Meta:
        model = SalesTab
        fields = '__all__'

    def create(self, validated_data):
        customer_data = validated_data.pop('customer')
        location_data = customer_data.pop('location', None)
        customer_phone = customer_data['phone']

        # Create a new location if provided
        if location_data:
            location, created = Locations.objects.get_or_create(**location_data)
        else:
            location = None

        existing_customer = Customers.objects.filter(phone=customer_phone).first()

        if existing_customer:
            # Customer already exists, update their information
            existing_customer.location = location
            existing_customer.sales = customer_data['sales']
            existing_customer.save()
            sales_tab = SalesTab.objects.create(customer=existing_customer, **validated_data)
        else:
            # Create a new customer with the associated location
            customer = Customers.objects.create(location=location, **customer_data)

            # Create the sales tab with the newly created customer
            sales_tab = SalesTab.objects.create(customer=customer, **validated_data)
        expected_date_to_repay = validated_data.get('expected_date_to_repay')
        debt_amount = validated_data.get('debt_amount')
        if expected_date_to_repay and debt_amount:
            debt = Dbts.objects.create(
                sales_tab=sales_tab,
                customer=sales_tab.customer,
                amount=debt_amount,
                expected_date_to_repay=expected_date_to_repay
            )
            debt.save()        
        return sales_tab


   
class RecordOtherProductsSalesSerializer(serializers.ModelSerializer):
    customer = AddCustomerSerializer()

    class Meta:
        model = OtherProductsSalesTab
        fields = '__all__'

    def create(self, validated_data):
        customer_data = validated_data.pop('customer')
        location_data = customer_data.pop('location', None)
        customer_phone = customer_data['phone']

        # Create a new location if provided
        if location_data:
            location, created = Locations.objects.get_or_create(**location_data)
        else:
            location = None

        existing_customer = Customers.objects.filter(phone=customer_phone).first()

        if existing_customer:
            # Customer already exists, update their information
            existing_customer.location = location
            existing_customer.sales = customer_data['sales']
            existing_customer.save()
            sales_tab = OtherProductsSalesTab.objects.create(customer=existing_customer, **validated_data)
        else:
            # Create a new customer with the associated location
            customer = Customers.objects.create(location=location, **customer_data)

            # Create the sales tab with the newly created customer
            sales_tab = OtherProductsSalesTab.objects.create(customer=customer, **validated_data)
        expected_date_to_repay = validated_data.get('expected_date_to_repay')
        debt_amount = validated_data.get('debt_amount')
        if expected_date_to_repay and debt_amount:
            debt = OtherProductsDbts.objects.create(
                sales_tab=sales_tab,
                customer=sales_tab.customer,
                amount=debt_amount,
                expected_date_to_repay=expected_date_to_repay
            )
            debt.save()        
        return sales_tab





class AddProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cylinder
        fields = '__all__'

        def create(self, validated_data):
            product = Cylinder.objects.create(**validated_data)

            return product



class AssignedCylindersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedCylinders
        fields = ['id', 'cylinder', 'assigned_quantity', 'filled', 'empties', 'complete_sale', 'refill_sale', 'date_assigned']
       
class SalesTeamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfSalesTeam
        fields = '__all__'

class SalesTeamSerializer(serializers.ModelSerializer):
    type_of_sales_team = SalesTeamTypeSerializer()
    employees = AllEmployeesSerializer(many=True)
    class Meta:
        model = SalesTeam
        fields = '__all__'


class AssignedCylindersTeamSerializer(serializers.ModelSerializer):
    cylinder_details = serializers.SerializerMethodField()

    class Meta:
        model = AssignedCylinders
        fields = [
            'id', 
            'assigned_quantity',
            'filled', 'empties', 
            'complete_sale', 
            'refill_sale', 
            'date_assigned',
            'creator', 
            'sales_team', 
            'cylinder', 
            'cylinder_details',
            'spoiled',
            "wholesale_sold",
            "wholesale_refilled",
            "retail_sold",
            "retail_refilled",
        ]

    def get_cylinder_details(self, obj):
        return {
            "gas_type": obj.cylinder.cylinder.gas_type.name,
            "weight": obj.cylinder.cylinder.weight.weight,
        }


class all_sales_teamSerializer(serializers.ModelSerializer):
    employees = AllEmployeesSerializer(many=True)
    assigned_cylinders = serializers.SerializerMethodField()  # New field for assigned cylinders

    class Meta:
        model = SalesTeam
        fields = ['id', 'name', 'employees', 'assigned_cylinders', 'profile_image']

    def get_assigned_cylinders(self, obj):
        # assigned_cylinders = AssignedCylinders.objects.filter(sales_team=obj)
        assigned_cylinders = AssignedCylinders.objects.filter(sales_team=obj).select_related(
            "cylinder__cylinder__gas_type", 
            "cylinder__cylinder__weight"    
        )
        return AssignedCylindersTeamSerializer(assigned_cylinders, many=True).data


    

class AssignedCylindersSerializer(serializers.ModelSerializer):
    # cylinder = CylinderSerializer()
    class Meta:
        model = AssignedCylinders
        fields = '__all__'
        
 
class SalesSerializer(serializers.ModelSerializer):
    product = AssignedCylindersSerializer()
    class Meta:
        model = SalesTab
        fields = '__all__'




class AssignedCylinderSerializeDebt(serializers.ModelSerializer):
    gas_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.wholesale_selling_price", read_only=True)
    wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.wholesale_refil_price", read_only=True)
    retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.retail_selling_price", read_only=True)
    retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.retail_refil_price", read_only=True)

    min_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.min_wholesale_selling_price", read_only=True)
    min_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.min_wholesale_refil_price", read_only=True)
    min_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.min_retail_selling_price", read_only=True)
    min_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.min_retail_refil_price", read_only=True)
    
    max_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.max_wholesale_selling_price", read_only=True)
    max_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.max_wholesale_refil_price", read_only=True)
    max_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.max_retail_selling_price", read_only=True)
    max_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.max_retail_refil_price", read_only=True)

    class Meta:
        model = AssignedCylinders
        fields = [
            "id",
            "sales_team",
            "cylinder",
            "gas_type",  # Include gas type
            "weight",    # Include gas weight
            "assigned_quantity",
            "date_assigned",
            "filled",
            "empties",
            "wholesale_sold",
            "wholesale_refilled",
            "retail_sold",
            "retail_refilled",
            "transaction_complete",
            "spoiled",
            "wholesale_selling_price",
            "wholesale_refil_price",
            "retail_selling_price",
            "retail_refil_price",
            "min_wholesale_selling_price",
            "min_wholesale_refil_price",
            "min_retail_selling_price",
            "min_retail_refil_price",
            "max_wholesale_selling_price",
            "max_wholesale_refil_price",
            "max_retail_selling_price",
            "max_retail_refil_price"
        ]


class SalessSerializer(serializers.ModelSerializer):
    # product = AssignedCylindersSerializer()
    # sales_person = serializers.SerializerMethodField()
    product = AssignedCylinderSerializeDebt(read_only=True)
    # debt_info = serializers.SerializerMethodField()
    class Meta:
        model = SalesTab
        fields = '__all__'
        
class Debtorsserializer(serializers.ModelSerializer):
    sales_tab = SalessSerializer()
    class Meta:
        model = Dbts
        fields = '__all__'


class Customerserializer(serializers.ModelSerializer):
    customer_sales = SalessSerializer(many=True, read_only=True)
    customer_debt = Debtorsserializer(many=True, read_only=True)
    location = CustomerLocationSerializer()

    class Meta:
        model = Customers
        fields = '__all__'


class AllDebtorsSerializer(serializers.ModelSerializer):
    sales_tab = SalessSerializer()
    customer = Customerserializer()

    
    class Meta:
        model = Dbts
        fields = '__all__'
        
class SaleSerializer(serializers.ModelSerializer):
    # who_recorded_sale = EmployeesSerializer()
    # sales_agents = SalesTeamSerializer()
    customer = Customerserializer()
    product = AssignedCylindersSerializer()
    class Meta:
        model = SalesTab
        fields = '__all__'



class RecordMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'

    
    def create(self, validated_data):
        customers_data = validated_data.pop('customer')
        locations_data = validated_data.pop('location')

        # Create the message instance
        message = Messages.objects.create(**validated_data)
        message.customer.set(customers_data)
        message.location.set(locations_data)

        return message
    
    
    

class RecordBulkMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Messages
        fields = '__all__'

    
    def create(self, validated_data):
        # Extract customer and location data from the validated_data
        customers_data = validated_data.pop('customer')
        locations_data = validated_data.pop('location')

        # Create the message instance
        message = Messages.objects.create(**validated_data)

        # Add the related customers and locations to the message
        message.customer.set(customers_data)
        message.location.set(locations_data)

        return message
    
    
    

class CreateSalesTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTeam
        fields = ['profile_image', 'name']  # Add other fields as needed

    def create(self, validated_data):
        profile_image = self.context['request'].data.get('profile_image')  # Extract the image from the request
        validated_data['profile_image'] = profile_image

        salesteam = SalesTeam.objects.create(**validated_data)
        return salesteam


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class CylinderInStoreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cylinder
        fields = ['id', 'min_wholesale_selling_price', 'min_wholesale_refil_price', 
                  'min_retail_selling_price', 'min_retail_refil_price',  'max_wholesale_selling_price', 'max_wholesale_refil_price', 
                  'max_retail_selling_price', 'max_retail_refil_price', 'weight']



class CylinderStoreSerializer(serializers.ModelSerializer):
    cylinder_details = CylinderInStoreSerializer(source='cylinder', read_only=True)

    class Meta:
        model = CylinderStore
        fields = ['id', 'filled', 'empties','spoiled', 'total_cylinders', 'dates', 
                  'date_of_operation', 'cylinder_details']

class CylinderSerializer(serializers.ModelSerializer):
    stores = CylinderStoreSerializer(many=True, source='cylinderstore_set', read_only=True)
    weight = CylinderWeightSerializer()

    class Meta:
        model = Cylinder
        fields = ['id', 'gas_type', 'weight', 'stores']

class CylinderTypeSerializer(serializers.ModelSerializer):
    cylinders = CylinderSerializer(many=True, source='cylinder_set', read_only=True)

    class Meta:
        model = CylinderType
        fields = ['id', 'name', 'cylinders']


class OtherProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherProducts
        fields = '__all__'





class CylinderCreateSerializer(serializers.Serializer):
    gas_type = serializers.CharField()
    weight = serializers.IntegerField()
    min_wholesale_selling_price = serializers.IntegerField()
    min_wholesale_refil_price = serializers.IntegerField()
    min_retail_selling_price = serializers.IntegerField()
    min_retail_refil_price = serializers.IntegerField()
    max_wholesale_selling_price = serializers.IntegerField()
    max_wholesale_refil_price = serializers.IntegerField()
    max_retail_selling_price = serializers.IntegerField()
    max_retail_refil_price = serializers.IntegerField()
    filled = serializers.IntegerField()
    empties = serializers.IntegerField()
    spoiled = serializers.IntegerField()





class CreateOtherProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherProducts
        fields = '__all__'

    def create(self, validated_data):
        product = OtherProducts.objects.create(**validated_data)
        return product



class AssignedCylinderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedCylinders
        fields = ['id', 'creator', 'sales_team', 'cylinder', 'assigned_quantity', 'date_assigned']


    def validate(self, data):
        cylinder_store = data.get('cylinder')
        assigned_quantity = data['assigned_quantity']

        if assigned_quantity > cylinder_store.filled:
            raise serializers.ValidationError(
                f"Assigned quantity exceeds available filled cylinders ({cylinder_store.filled})."
            )
        return data

    def create(self, validated_data):
        # Reduce the number of filled cylinders
        cylinder_store = validated_data['cylinder']
        assigned_quantity = validated_data['assigned_quantity']

        if cylinder_store.filled >= assigned_quantity:
            cylinder_store.filled -= assigned_quantity
            cylinder_store.save()
        else:
            raise serializers.ValidationError(
                "Not enough filled cylinders available to assign."
            )

        # Create the AssignedCylinders instance
        assigned_cylinder = AssignedCylinders.objects.create(**validated_data)
        return assigned_cylinder
    


class AssignedCylinderSerializerrr(serializers.ModelSerializer):
    gas_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    sales_team = CreateSalesTeamSerializer(read_only=True)
    wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.wholesale_selling_price", read_only=True)
    wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.wholesale_refil_price", read_only=True)
    retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.retail_selling_price", read_only=True)
    retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.retail_refil_price", read_only=True)

    min_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.min_wholesale_selling_price", read_only=True)
    min_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.min_wholesale_refil_price", read_only=True)
    min_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.min_retail_selling_price", read_only=True)
    min_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.min_retail_refil_price", read_only=True)
    

    mid_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.mid_wholesale_selling_price", read_only=True)
    mid_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.mid_wholesale_refil_price", read_only=True)
    mid_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.mid_retail_selling_price", read_only=True)
    mid_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.mid_retail_refil_price", read_only=True)
    
    max_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.max_wholesale_selling_price", read_only=True)
    max_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.max_wholesale_refil_price", read_only=True)
    max_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.max_retail_selling_price", read_only=True)
    max_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.max_retail_refil_price", read_only=True)

    class Meta:
        model = AssignedCylinders
        fields = [
            "id",
            "sales_team",
            "cylinder",
            "gas_type",  # Include gas type
            "weight",    # Include gas weight
            "assigned_quantity",
            "date_assigned",
            "filled",
            "empties",
            "less_pay",
            "filled_lost",
            "empties_lost",
            "wholesale_sold",
            "wholesale_refilled",
            "retail_sold",
            "retail_refilled",
            "transaction_complete",
            "spoiled",
            "wholesale_selling_price",
            "wholesale_refil_price",
            "retail_selling_price",
            "retail_refil_price",
            "min_wholesale_selling_price",
            "min_wholesale_refil_price",
            "min_retail_selling_price",
            "min_retail_refil_price",
            "mid_wholesale_selling_price",
            "mid_wholesale_refil_price",
            "mid_retail_selling_price",
            "mid_retail_refil_price",
            "max_wholesale_selling_price",
            "max_wholesale_refil_price",
            "max_retail_selling_price",
            "max_retail_refil_price"
        ]

class AssignedCylinderSerializerDefaulted(serializers.ModelSerializer):
    gas_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.wholesale_selling_price", read_only=True)
    wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.wholesale_refil_price", read_only=True)
    retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.retail_selling_price", read_only=True)
    retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.retail_refil_price", read_only=True)

    min_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.min_wholesale_selling_price", read_only=True)
    min_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.min_wholesale_refil_price", read_only=True)
    min_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.min_retail_selling_price", read_only=True)
    min_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.min_retail_refil_price", read_only=True)
    
    max_wholesale_selling_price = serializers.IntegerField(source="cylinder.cylinder.max_wholesale_selling_price", read_only=True)
    max_wholesale_refil_price = serializers.IntegerField(source="cylinder.cylinder.max_wholesale_refil_price", read_only=True)
    max_retail_selling_price = serializers.IntegerField(source="cylinder.cylinder.max_retail_selling_price", read_only=True)
    max_retail_refil_price = serializers.IntegerField(source="cylinder.cylinder.max_retail_refil_price", read_only=True)

    class Meta:
        model = AssignedCylinders
        fields = [
            "id",
            "sales_team",
            "cylinder",
            "gas_type",  # Include gas type
            "weight",    # Include gas weight
            "assigned_quantity",
            "date_assigned",
            "filled",
            "empties",
            "less_pay",
            "filled_lost",
            "empties_lost",
            "wholesale_sold",
            "wholesale_refilled",
            "retail_sold",
            "retail_refilled",
            "transaction_complete",
            "spoiled",
            "wholesale_selling_price",
            "wholesale_refil_price",
            "retail_selling_price",
            "retail_refil_price",
            "min_wholesale_selling_price",
            "min_wholesale_refil_price",
            "min_retail_selling_price",
            "min_retail_refil_price",
            "max_wholesale_selling_price",
            "max_wholesale_refil_price",
            "max_retail_selling_price",
            "max_retail_refil_price"
        ]

class LostCylindersSerializer(serializers.ModelSerializer):
    cylinder = AssignedCylinderSerializerDefaulted(read_only = True)
    class Meta:
        model = CylinderLost
        fields = '__all__'


class LessPayCylindersSerializer(serializers.ModelSerializer):
    cylinder = AssignedCylinderSerializerDefaulted(read_only = True)
    class Meta:
        model = CylinderLessPay
        fields = '__all__'


class AssignedCylinderReceiptSerializer(serializers.ModelSerializer):
    gas_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    sales_team = CreateSalesTeamSerializer(read_only=True)
    
    class Meta:
        model = AssignedCylindersRecipt
        fields = [
            "id",
            "sales_team",
            "cylinder",
            "gas_type",  # Include gas type
            "weight",    # Include gas weight
            "assigned_quantity",
            "date_assigned",
        ]


class AssignedOtherProductReceiptSerializer(serializers.ModelSerializer):
    # gas_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    # weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    product = OtherProductsSerializer(read_only=True)
    sales_team = CreateSalesTeamSerializer(read_only=True)
    
    class Meta:
        model = AssignedOtherProductRecipt
        fields = [
            "id",
            "sales_team",
            "product",
            "assigned_quantity",
            "date_assigned",
        ]



class ReturnCylinderReceiptSerializer(serializers.ModelSerializer):
    gas_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    sales_team = CreateSalesTeamSerializer(read_only=True)
    
    class Meta:
        model = ReturnClylindersReciept
        fields = [
            "id",
            "sales_team",
            "cylinder",
            "gas_type",  # Include gas type
            "weight",    # Include gas weight
            "spoiled",
            "filled",
            "empties",
            "empties_lost",
            "filled_lost",
            "less_pay",
            "date_collected",
        ]



class AssignedOtherProductSerializer(serializers.ModelSerializer):
    
    sales_team = CreateSalesTeamSerializer(read_only=True)
    product = OtherProductsSerializer(read_only=True)
    
    class Meta:
        model = AssignedOtherProducts
        fields = [
            "id",
            "sales_team",
            "product",

            "assigned_quantity",
            "date_assigned",
        
        ]


class BulkAssignedCylinderSerializer(serializers.Serializer):
    sales_team = serializers.PrimaryKeyRelatedField(queryset=SalesTeam.objects.all())
    cylinder = serializers.PrimaryKeyRelatedField(queryset=CylinderStore.objects.all())
    assigned_quantity = serializers.IntegerField()

    def validate(self, data):
        cylinder_store = data.get('cylinder')
        assigned_quantity = data['assigned_quantity']

        if assigned_quantity > cylinder_store.filled:
            raise serializers.ValidationError(
                f"Assigned quantity exceeds available filled cylinders ({cylinder_store.filled})."
            )
        return data


class BulkAssignedOtherProductsSerializer(serializers.Serializer):
    sales_team = serializers.PrimaryKeyRelatedField(queryset=SalesTeam.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset = OtherProducts.objects.all())
    assigned_quantity = serializers.IntegerField()

    def validate(self, data):
        product_store = data.get('product')
        assigned_quantity = data['assigned_quantity']

        if assigned_quantity > product_store.quantity:
            raise serializers.ValidationError(
                f"Assigned quantity exceeds available quantity ({product_store.quantity})."
            )
        return data


class ReturnCylindersSerializer(serializers.ModelSerializer):
    cylinder_type = serializers.CharField(source="cylinder.cylinder.gas_type.name", read_only=True)
    weight = serializers.IntegerField(source="cylinder.cylinder.weight.weight", read_only=True)
    id = serializers.IntegerField(required=True)
    class Meta:
        model = AssignedCylinders
        fields = [
            "id", 
            "cylinder_type",  # Cylinder type name
            "weight",         # Cylinder weight
            "assigned_quantity",
            "filled",
            "empties",
            "transaction_complete",
            "spoiled"
        ]


class MyProfileSerializer(serializers.ModelSerializer):
    sales_team = SalesTeamSerializer()
    class Meta:
        model = Employees
        fields = '__all__'

class CreateMyProfileSerializer(serializers.ModelSerializer):
    # sales_team = SalesTeamSerializer()
    class Meta:
        model = Employees
        fields = '__all__'



class SalesRecordSerializer(serializers.ModelSerializer):
    # sales_person = serializers.CharField(source='sales_person.email', read_only=True)
    sales_person = serializers.SerializerMethodField()
    customer = Customerserializer(read_only=True)
    product = AssignedCylinderSerializerrr(read_only=True)
    debt_info = serializers.SerializerMethodField()

    class Meta:
        model = SalesTab
        fields = '__all__'



    def get_sales_person(self, obj):
        try:
            # Get the employee related to the sales_person
            employee = Employees.objects.get(user=obj.sales_person)
            return AllEmployeesSerializer(employee).data
        except Employees.DoesNotExist:
            return None
        

    def get_debt_info(self, obj):
        debt = Dbts.objects.filter(sales_tab=obj).first()
        if debt:
            return {
                "debt_amount": debt.amount,
                "expected_date_to_repay": debt.expected_date_to_repay,
            }
        return None




class CylinderLostResolveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CylinderLost
        fields = ['resolved']

    def update(self, instance, validated_data):
        """Mark a CylinderLost instance as resolved."""
        instance.resolved = validated_data.get('resolved', instance.resolved)
        instance.save()
        return instance
    


class ExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = '__all__'


    


class AdvancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advances
        fields = '__all__'


class CylinderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CylinderRequestTransfer
        fields = '__all__'