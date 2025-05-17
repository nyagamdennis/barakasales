from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from Business.models import BusinessDetails



class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not phone_number:
            raise ValueError('The Phone number field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone_number, password, **extra_fields)
    
    

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)


    is_owner = models.BooleanField(default=False)  # Business owner role
    is_employee = models.BooleanField(default=False)
    business = models.ForeignKey(
        BusinessDetails,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)
    
    
    
    objects = CustomUserManager()


    class Meta:
        permissions = [
            ("is_employee", "Can act as an employee"),
            ("is_owner", "Can act as a business owner"),
        ]


    def __str__(self):
        return f"{self.email} ({'Owner' if self.is_owner else 'Employee'})"


# print("App Label for CustomUser:", CustomUser._meta.app_label)