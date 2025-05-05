from django.urls import path
from . import views


urlpatterns = [
    path('', views.BusinessManagement.as_view(), name=''),

]