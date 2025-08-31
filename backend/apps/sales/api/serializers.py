from rest_framework import serializers
from ..models import DailySales

class SalesSerializer(serializers.ModelSerializer):
    registered_by = serializers.StringRelatedField(read_only=True)
    calculated_commission = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    commission_rate_display = serializers.SerializerMethodField()

    class Meta:
        model = DailySales
        fields = [
            'seller',
            'sale_date',
            'total_amount',
            'commission_rate_applied',  # valor decimal real no POST/PUT
            'commission_rate_display',  # mostra "0,5%" no GET
            'calculated_commission',
            'notes',
            'registered_by',
        ]
        read_only_fields = ['registered_by', 'calculated_commission', 'commission_rate_display']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user

        # vendedores comuns não podem editar a taxa
        if user.user_type not in ['ADMIN', 'MANAGER']:
            self.fields['commission_rate_applied'].read_only = True

    def get_commission_rate_display(self, obj):
        # Formata 0.5 -> "0,5%"
        return f"{obj.commission_rate_applied:.2f}%"

    def create(self, validated_data):
        validated_data['registered_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['registered_by'] = self.context['request'].user
        return super().update(instance, validated_data)
