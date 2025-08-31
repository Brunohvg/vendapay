# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import BaseModel
from django.db.models import Sum, F, DecimalField
class Account(AbstractUser, BaseModel):
    """
    Modelo de usuário customizado.
    
    Herda de:
    - AbstractUser: username, email, password, first_name, last_name, etc.
    - BaseModel: id, uuid, is_active, timestamps
    
    Para o sistema de comissões, o importante é identificar quem são os VENDEDORES.
    """
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        SELLER = 'SELLER', 'Vendedor'
        MANAGER = 'MANAGER', 'Gerente'
    
    user_type = models.CharField(
        max_length=10, 
        choices=UserType.choices, 
        default=UserType.SELLER,
        verbose_name="Tipo de Usuário",
        help_text="Define o papel do usuário no sistema"
    )
    
    # Campos adicionais úteis
    document = models.CharField(
        max_length=14, 
        unique=True, 
        verbose_name="CPF/CNPJ",
        help_text="Apenas números"
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name="Telefone"
    )
    
    # Controles específicos para comissão
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.50,
        verbose_name="Taxa de Comissão (%)",
        help_text="Percentual de comissão que este vendedor recebe (padrão: 0.5%)"
    )
    commission_active = models.BooleanField(
        default=True,
        verbose_name="Comissão Ativa",
        help_text="Se desabilitado, este vendedor não receberá comissões"
    )
    commission_start_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name="Início das Comissões",
        help_text="Data a partir da qual este vendedor começou a receber comissões"
    )
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def is_seller(self):
        """Verifica se o usuário é um vendedor ativo para comissões."""
        return (
            self.user_type == self.UserType.SELLER and 
            self.commission_active and 
            self.is_active
        )
    
    def total_sold(self, start_date=None, end_date=None):
        qs = self.daily_sales.filter(is_active=True)
        if start_date:
            qs = qs.filter(sale_date__gte=start_date)
        if end_date:
            qs = qs.filter(sale_date__lte=end_date)
        result = qs.aggregate(total=Sum('total_amount'))
        return result['total'] or 0

    def total_commission_paid(self, start_date=None, end_date=None):
        qs = self.daily_sales.filter(is_active=True)
        if start_date:
            qs = qs.filter(sale_date__gte=start_date)
        if end_date:
            qs = qs.filter(sale_date__lte=end_date)
        result = qs.aggregate(total=Sum('calculated_commission'))
        return result['total'] or 0
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        indexes = [
            # Índice para consultas de vendedores ativos
            models.Index(fields=['user_type', 'commission_active', 'is_active']),
        ]