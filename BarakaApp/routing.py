from django.urls import re_path
from .consumers import EmployeeStatusConsumer


websocket_urlpatterns = [
    re_path(r'ws/employee-status/(?P<employee_id>\d+)/$', EmployeeStatusConsumer.as_asgi()),

]
