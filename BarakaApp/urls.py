from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('customer/', views.customers, name='customers'),
    path('debtors/', views.debtors, name='debtors'),
    path('sales/', views.sales_func, name='sales'),
    path('locations/', views.location_func, name='location'),
    path('products/', views.product_func, name='product'),
    path('addcustomer/', views.add_customer, name='add-customer'),
    path('recordsales/', views.record_sales, name='record-sales'),
    path('employees/', views.all_employees, name='all-employees'),
    path('assignedcylider/', views.assignedProduct, name='assigned-cylinder'),
    path('assignedproduct/', views.assignedOtherProduct, name='assigned-product'),
    path('sendsms/', views.sendsms, name='send-sms'),
    path('sendbulksms/', views.sendbulksms, name='send-bulk-sms'),
    path('getsalesteam/', views.get_sales_team, name='sales-team'),
    path('addassignedcylinder/', views.assign_products, name = 'add_assigned_product'),
    path('sales-team-management/', views.sales_team_management, name='sales-team-management'),
    path('update_assigned_quantity/<str:pk>/', views.update_assigned_quantity, name='update_assigned_quantity'),
    path('createteam/', views.createteam),
    # path('business/<int:pk>', views.BusinessOperations.as_view()),
    path('store/', views.Stores, name='store'),
    path('other-products/', views.OtherProductsViews.as_view(), name='store'),
    path('refill/', views.RefillOperations.as_view()),
    path('addnewcylinder/', views.AddNewCylinder.as_view()),
    path('updateCylinder/<str:pk>/', views.CylinderOperations.as_view()),
    path('addanothercylinder/<str:pk>/', views.AnotherCylinder.as_view()),
    path('assign-cylinders/', views.BulkAssignCylinderView.as_view(), name='assign-cylinders'),
    path('the-assigned-cylinders/', views.AssignedCylindersListView.as_view(), name='assigned-cylinders-list'),
    path('return-assigned-cylinders/', views.ReturnAssignedCylindersView.as_view(), name='return-assigned-cylinders'),
    path('return-all-assigned-cylinders/', views.ReturnAllAssignedCylindersView.as_view(), name='return-all-assigned-cylinders'),
    path('addspoiled/', views.addassignedProductSpoiled),
    path('updatespoiled/', views.updateassignedProductSpoiled),
    path('myprofile/', views.MyProfiles.as_view()),
    path('salesteamdata/', views.SalesRecordsView.as_view()),
    path('adminsalesteamdata/', views.AdminSalesRecordsView.as_view()),
    path('adminsverifyalesteamdata/<str:sale_id>/', views.AdminVerifySalesRecordsView.as_view()),
    path('check-user-status/', views.CheckUserStatusView.as_view()),
    path('transfer/<str:employee_id>/', views.transfer_employee),
    path('update-status/<str:employee_id>/', views.update_employee_status),
]

# urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)