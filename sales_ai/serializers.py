from rest_framework import serializers
from .models import *
from BarakaApp.serializers import SalesTeamSerializer



class SalesReportSerializer(serializers.ModelSerializer):
    sales_team = SalesTeamSerializer()
    class Meta:
        model = SalesReport
        fields = '__all__'



class RefillCostAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefillCostAnalysis
        fields = '__all__'


class CompanyExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyExpenses
        fields = '__all__'