# apps/accounts/api/serializers.py

from rest_framework import serializers
from ..models import Account

class AccountsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'user_type', 'document', 'phone',
            'commission_rate', 'commission_active', 'commission_start_date',
            'is_active', 'password', 'full_name',
        ]
        
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': False, 'allow_blank': True},
            'email': {'required': True},
        }

    def get_full_name(self, obj):
        return obj.get_full_name()

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.setdefault('last_name', '')
        user = Account(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance
