from rest_framework import serializers
from ..models import DailySales

class SalesSerializer(serializers):
    class Meta:
        model = DailySales
        fields = ('total_amount', )