from django.db import models
from users.models import CustomUser
from datetime import datetime


class ProductCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Locations(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name



class OtherProducts(models.Model):
    name = models.CharField(max_length=200)
    whole_sales_price = models.PositiveIntegerField(default=0)
    retail_sales_price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    date_of_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CylinderWeight(models.Model):
    weight =  models.IntegerField()
    
    def __str__(self):
        return f'{self.weight}(Kg)'
    

    
class CylinderType(models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class Cylinder(models.Model):
    gas_type = models.ForeignKey(CylinderType, on_delete=models.CASCADE)
    weight = models.ForeignKey(CylinderWeight, on_delete=models.CASCADE)
    min_wholesale_selling_price = models.PositiveIntegerField(default=0)
    min_wholesale_refil_price = models.PositiveIntegerField(default=0)
    min_retail_selling_price = models.PositiveIntegerField(default=0)
    min_retail_refil_price = models.PositiveIntegerField(default=0)
    max_wholesale_selling_price = models.PositiveIntegerField(default=0)
    max_wholesale_refil_price = models.PositiveIntegerField(default=0)
    max_retail_selling_price = models.PositiveIntegerField(default=0)
    max_retail_refil_price = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f'{self.gas_type.name} {self.weight.weight}'


class CylinderStore(models.Model):
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE)
    filled = models.PositiveIntegerField(default=0)
    empties = models.PositiveIntegerField(default=0)
    spoiled = models.PositiveIntegerField(default=0)
    total_cylinders = models.PositiveIntegerField(default=0)
    dates = models.DateTimeField()
    date_of_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.cylinder.gas_type.name} {self.cylinder.weight.weight}kg - empties:{self.empties} - filled:{self.filled}"





class Employees(models.Model):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    
    gender_choice = [
        (MALE, 'Male'),
        (FEMALE,'Female')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    alternative_phone = models.CharField(max_length=15 ,null=True, blank=True)
    gender = models.CharField(max_length=200, choices=gender_choice)
    profile_image = models.ImageField(upload_to='profile', null=True, blank=True)
    front_id = models.ImageField(upload_to='id_pictures', null=True, blank=True)
    back_id = models.ImageField(upload_to='id_pictures', blank=True, null=True)
    sales_team = models.ForeignKey(
        'SalesTeam',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'  # Allows reverse lookup from SalesTeam to Employees
    )
    verified = models.BooleanField(default=False)
    defaulted = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    fired = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        permissions = [
            ("employee_permission", "Can act as an employee")
        ]

class DefaultedProducts(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    cylinder = models.ForeignKey(CylinderStore, on_delete=models.CASCADE, null=True, blank=True)
    other_products = models.ForeignKey(OtherProducts, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.PositiveIntegerField()
    cleared = models.BooleanField(default=False)


    def __str__(self):
        return self.emplyee



class TypeOfSalesTeam(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name
    

class SalesTeam(models.Model):
    type_of_sales_team = models.ForeignKey(TypeOfSalesTeam, on_delete=models.CASCADE, null=True, blank=True)
    profile_image = models.ImageField(upload_to='sales_team_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    # employees = models.ManyToManyField(Employees, related_name='sales_teams', blank=True)  # Specify a related_name
    date_created = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.name
    
    
class AssignedCylinders(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.CASCADE, related_name='salesTeam')
    cylinder = models.ForeignKey(CylinderStore, on_delete=models.CASCADE)
    assigned_quantity = models.PositiveIntegerField(default=0)
    spoiled = models.PositiveIntegerField(default=0)
    filled = models.PositiveIntegerField(default=0)
    empties = models.PositiveIntegerField(default=0)
    filled_lost = models.PositiveIntegerField(default=0)
    empties_lost = models.PositiveIntegerField(default=0)
    wholesale_sold = models.PositiveIntegerField(default=0)
    wholesale_refilled = models.PositiveIntegerField(default=0)
    retail_sold = models.PositiveIntegerField(default=0)
    retail_refilled = models.PositiveIntegerField(default=0)
    complete_sale = models.PositiveIntegerField(default=0)
    refill_sale = models.PositiveIntegerField(default=0)
    missing_cylinder = models.PositiveIntegerField(default=0)
    less_pay = models.PositiveIntegerField(default=0)
    transaction_complete = models.BooleanField(default=False)
    date_assigned = models.DateTimeField(auto_now_add=True)


    def return_cylinders(self):
        filled_returned = (self.filled - self.filled_lost)
        empties_returned = self.empties
        filled_lost_returned = self.filled_lost
        empties_lost_returned = self.empties_lost
        spoiled_returned = self.spoiled
        less_pay_returned = self.less_pay

        # Update CylinderStore counts
        self.filled -= self.filled_lost
        self.assigned_quantity = (self.filled - self.filled_lost - self.less_pay)
        self.cylinder.spoiled += self.spoiled
        self.cylinder.empties += (self.empties - self.empties_lost + self.less_pay)
        
        self.cylinder.save()

        # Mark transaction as complete
        # self.transaction_complete = True
        self.spoiled = 0
        self.empties = 0
        self.empties_lost = 0
        self.filled_lost = 0
        self.less_pay = 0
        self.save()

        return filled_returned, empties_returned, spoiled_returned, filled_lost_returned, empties_lost_returned, less_pay_returned



    def return_all_cylinders(self):
        filled_returned = self.filled
        empties_returned = self.empties
        filled_lost_returned = self.filled_lost
        empties_lost_returned = self.empties_lost
        spoiled_returned = self.spoiled
        less_pay_returned = self.less_pay

        # Update CylinderStore counts
        self.cylinder.filled += (self.filled - self.filled_lost - self.less_pay)
        self.cylinder.spoiled += self.spoiled
        self.cylinder.empties += (self.empties - self.empties_lost + self.less_pay)
        self.cylinder.save()

        # Mark transaction as complete
        self.transaction_complete = True
        self.spoiled = 0
        self.empties = 0
        self.filled = 0
        self.empties_lost = 0
        self.filled_lost = 0
        self.assigned_quantity = 0
        self.less_pay = 0
        self.save()

        return filled_returned, empties_returned, spoiled_returned, empties_lost_returned, filled_lost_returned, less_pay_returned


class ReturnClylindersReciept(models.Model):
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.SET_NULL, null=True, blank=True)
    cylinder = models.ForeignKey(CylinderStore, on_delete=models.SET_NULL, null=True, blank=True)
    filled = models.PositiveIntegerField(default=0)
    empties = models.PositiveIntegerField(default=0)
    spoiled = models.PositiveIntegerField(default=0)
    less_pay = models.PositiveIntegerField(default=0)
    
    empties_lost = models.PositiveIntegerField(default=0)
    filled_lost = models.PositiveIntegerField(default=0)
    
    print_complete = models.BooleanField(default=False)
    date_collected = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.empties

class AssignedCylindersRecipt(models.Model):
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.SET_NULL, null=True, blank=True)
    cylinder = models.ForeignKey(CylinderStore, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_quantity = models.PositiveIntegerField(default=0)
    # empties_lost = models.PositiveIntegerField(default=0)
    # filled_lost = models.PositiveIntegerField(default=0)
    print_complete = models.BooleanField(default=False)
    date_assigned = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.assigned_quantity




class AssignedOtherProducts(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.CASCADE, related_name='other_products_salesTeam')
    product = models.ForeignKey(OtherProducts, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_quantity = models.PositiveIntegerField(default=0)
    spoiled = models.PositiveIntegerField(default=0)
    wholesale_sold = models.PositiveIntegerField(default=0)
    retail_sold = models.PositiveIntegerField(default=0)
    missing_products = models.PositiveIntegerField(default=0)
    transaction_complete = models.BooleanField(default=False)
    date_assigned = models.DateTimeField(auto_now_add=True)



class AssignedOtherProductRecipt(models.Model):
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(OtherProducts, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_quantity = models.PositiveIntegerField(default=0)
    print_complete = models.BooleanField(default=False)
    date_assigned = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.assigned_quantity




class CylinderLost(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, blank=True)
    cylinder = models.ForeignKey(AssignedCylinders, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_empty_cylinder = models.PositiveIntegerField(default=0)
    number_of_filled_cylinder = models.PositiveIntegerField(default=0)
    resolved = models.BooleanField(default=False)
    date_lost = models.DateTimeField(auto_now_add=True)

    # def __str__(Self):
    #     return Self.employee

class CylinderLessPay(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, blank=True)
    cylinder = models.ForeignKey(AssignedCylinders, on_delete=models.SET_NULL, null=True, blank=True)
    cylinders_less_pay = models.PositiveIntegerField(default=0)
    resolved = models.BooleanField(default=False)
    date_lost = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.employee


class Customers(models.Model):
    WHOLESALE = "WHOLESALE"
    RETAIL = "RETAIL"
    SALES_CHOICES = [
        (WHOLESALE, "Wholesale"),
        (RETAIL, "Retail"),
    ]
    # creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sales = models.CharField(max_length=200,choices=SALES_CHOICES)
    name = models.CharField(max_length=200)
    phone = models.IntegerField()
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    date_aded = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f'{self.name}, {self.sales} customer, from {self.location.name}'
   
    
class TypeOfSale(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
    
        
class SalesTab(models.Model):
    COMPLETESALE = "COMPLETESALE"
    REFILL = "REFILL"
    SALES_TYPE = [
        (COMPLETESALE, "completeSale"),
        (REFILL, "refillSale"),
    ]
    WHOLESALE = "WHOLESALE"
    RETAIL = "RETAIL"
    SALES_CHOICES = [
        (WHOLESALE, "Wholesale"),
        (RETAIL, "Retail"),
    ]
    sales_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='customer_sales' )
    product = models.ForeignKey(AssignedCylinders, on_delete=models.CASCADE, null=True, blank=True)
    store_product = models.ForeignKey(CylinderStore, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    sales_type = models.CharField(choices=SALES_TYPE, max_length=200, null=True)
    sales_choice = models.CharField(choices=SALES_CHOICES, max_length=200, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    partial_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,  null=True, blank=True)
    debt_amount = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_fully_paid = models.BooleanField(default=False)
    exchanged_with_local = models.BooleanField(default=False)
    expected_date_to_repay = models.DateField(blank=True, null=True)
    sales_person_payment_verified = models.BooleanField(default=False)
    admin_payment_verified = models.BooleanField(default=False)
    date_sold = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.customer.name} bought {self.quantity}'

class OtherProductsSalesTab(models.Model):
    WHOLESALE = "WHOLESALE"
    RETAIL = "RETAIL"
    SALES_CHOICES = [
        (WHOLESALE, "Wholesale"),
        (RETAIL, "Retail"),
    ]
    sales_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='customer_other_products_sales' )
    product = models.ForeignKey(AssignedOtherProducts, on_delete=models.CASCADE, null=True, blank=True)
    store_product = models.ForeignKey(OtherProducts, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    sales_choice = models.CharField(choices=SALES_CHOICES, max_length=200, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    partial_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,  null=True, blank=True)
    debt_amount = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_fully_paid = models.BooleanField(default=False)
    expected_date_to_repay = models.DateField(blank=True, null=True)
    admin_payment_verified = models.BooleanField(default=False)
    date_sold = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.customer.name} bought {self.quantity}'
    
class Dbts(models.Model):
    # authorized_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_debt')
    sales_tab = models.ForeignKey(SalesTab, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    date_given = models.DateField(auto_now_add=True)
    expected_date_to_repay = models.DateField()
    cleared = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.customer.name} has a debt of {self.amount}'
    
    
class OtherProductsDbts(models.Model):
    # authorized_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    sales_team = models.ForeignKey(SalesTeam, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True, related_name='customerdebt')
    sales_tab = models.ForeignKey(SalesTab, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    date_given = models.DateField(auto_now_add=True)
    expected_date_to_repay = models.DateField()
    cleared = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.customer.name} has a debt of {self.amount}'
    
    
class CreditTransaction(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f'{self.customer.name} paid {self.amount}'
        
class Messages(models.Model):
    # business = models.ForeignKey(Business, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    customer = models.ManyToManyField(Customers, blank=True)
    employees = models.ManyToManyField(Employees, blank=True)
    location = models.ManyToManyField(Locations,  blank=True)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.message[:150]}..."