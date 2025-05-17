from django.urls import path
from . import views


urlpatterns = [
    path('', views.BusinessManagement.as_view(), name=''),
    path('operation/', views.BusinessOperation.as_view()),
    path('subscription/<str:pk>/', views.BusinessSubscription.as_view(), name='business-subscription'),
    path('subscription-free-trial/<str:pk>/', views.BusinessSubscriptionFreeTrial.as_view(), name='business-subscription-free-trial'),
    path('payments/<str:pk>/', views.SubscriptionPaymentsView.as_view()),
    path('mpesa-confirm/', views.MpesaConfirmation.as_view(), name='mpesa-confirmation'),
]