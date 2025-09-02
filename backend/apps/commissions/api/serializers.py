from rest_framework import serializers
from ..models import MonthlyCommissionReport

class MonthlyCommissionReportSerializer(serializers.ModelSerializer):
    period_display = serializers.ReadOnlyField()
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, default=None)

    class Meta:
        model = MonthlyCommissionReport
        fields = [
            'id', 'seller', 'year', 'month',
            'total_sales_amount', 'sales_days_count',
            'total_commission', 'average_commission_rate',
            'status', 'approved_by', 'approved_by_name', 'approved_at',
            'paid_at',
            'payment_notes', 'period_display'
        ]

        read_only_fields = [
            'total_sales_amount', 'sales_days_count',
            'total_commission', 'average_commission_rate',
            'approved_at', 'paid_at',
            'approved_by_name'
        ]

        extra_kwargs = {
            'approved_by': {'write_only': True, 'required': False, 'allow_null': True},
        }