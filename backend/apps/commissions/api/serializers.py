from rest_framework import serializers
from ..models import MonthlyCommissionReport

class MonthlyCommissionReportSerializer(serializers.ModelSerializer):
    period_display = serializers.ReadOnlyField()

    class Meta:
        model = MonthlyCommissionReport
        fields = [
            'id', 'seller', 'year', 'month',
            'total_sales_amount', 'sales_days_count',
            'total_commission', 'average_commission_rate',
            'status', 'approved_by', 'approved_at',
            'paid_at',
            'payment_notes', 'period_display'
        ]

        read_only_fields = [
            'total_sales_amount', 'sales_days_count',
            'total_commission', 'average_commission_rate',
            'approved_at', 'paid_at'
        ]

