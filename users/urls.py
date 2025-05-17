from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from .views import MyTokenObtainPairView, CustomTokenRefreshView
from rest_framework_simplejwt.views import (TokenRefreshView)



urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.user_registration, name='user-registration'),
    path('transfer/', views.TransferUser.as_view())
]