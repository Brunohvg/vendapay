from django.db import models
from rest_framework import serializers
from ..models import Account


class AccountsSerializer(serializers.ModelSerializer):
    """
    Serializer principal para Accounts.
    - Inclui o campo extra `full_name`.
    - Permite criação com senha.
    - Atualização de senha é opcional.
    - Mostra totais vendidos e comissão paga, filtráveis por múltiplos parâmetros.
    - Exibe flags de staff/superuser para identificar administradores.
    """
    full_name = serializers.SerializerMethodField(read_only=True)
    total_sold = serializers.SerializerMethodField(read_only=True)
    total_commission_paid = serializers.SerializerMethodField(read_only=True)

    def get_full_name(self, obj):
        return obj.get_full_name()

    def _get_date_filtered_qs(self, obj):
        """
        Retorna o queryset de vendas do vendedor filtrado por:
        - start_date
        - end_date
        - month
        - year
        Recebe os parâmetros via query_params.
        """
        qs = obj.daily_sales.filter(is_active=True)
        params = self.context["request"].query_params

        start = params.get("start_date")
        end = params.get("end_date")
        month = params.get("month")
        year = params.get("year")

        if start:
            qs = qs.filter(sale_date__gte=start)
        if end:
            qs = qs.filter(sale_date__lte=end)
        if year and year.isdigit():
            qs = qs.filter(sale_date__year=int(year))
        if month and month.isdigit():
            qs = qs.filter(sale_date__month=int(month))

        return qs

    def get_total_sold(self, obj):
        qs = self._get_date_filtered_qs(obj)
        result = qs.aggregate(total=models.Sum("total_amount"))
        return result["total"] or 0

    def get_total_commission_paid(self, obj):
        qs = self._get_date_filtered_qs(obj)
        result = qs.aggregate(total=models.Sum("calculated_commission"))
        return result["total"] or 0

    class Meta:
        model = Account
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "user_type", "document", "phone",
            "commission_rate", "commission_active", "commission_start_date",
            "is_active", "password",
            "is_staff", "is_superuser",   # 🔹 agora visíveis
            "full_name", "total_sold", "total_commission_paid",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "first_name": {"required": True},
            "last_name": {"required": False, "allow_blank": True},
            "email": {"required": True},
            "is_staff": {"read_only": True},      # 🔒 só pode ser alterado por endpoint específico
            "is_superuser": {"read_only": True},  # 🔒 idem
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        validated_data.setdefault("last_name", "")
        user = Account(**validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para o endpoint de troca de senha.
    - `old_password` é obrigatório e verificado.
    - `new_password` é a nova senha do usuário.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
