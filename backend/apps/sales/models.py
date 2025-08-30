# apps/sales/models.py
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel

class DailySales(BaseModel):
    """
    Registra o total de vendas que um vendedor fez em um dia específico.
    
    FLUXO:
    1. Vendedor faz vendas durante o dia
    2. No final do dia, vendedor lança o TOTAL vendido no sistema
    3. Sistema calcula automaticamente a comissão baseada na taxa do vendedor
    
    Exemplo:
    - Vendedor João vendeu R$ 1.000,00 no dia 15/01/2025
    - Taxa dele é 0.5%
    - Comissão = R$ 1.000,00 * 0.5% = R$ 5,00
    """
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # PROTECT: não permite deletar vendedor com vendas
        related_name='daily_sales',
        verbose_name="Vendedor",
        help_text="Vendedor que realizou as vendas"
    )
    
    sale_date = models.DateField(
        verbose_name="Data das Vendas",
        help_text="Data em que as vendas foram realizadas"
    )
    
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Total Vendido (R$)",
        help_text="Soma de todas as vendas do vendedor neste dia"
    )
    
    commission_rate_applied = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Taxa de Comissão Aplicada (%)",
        help_text="Taxa que foi aplicada no momento do lançamento (histórico)"
    )
    
    calculated_commission = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        verbose_name="Comissão Calculada (R$)",
        help_text="Valor da comissão = total_amount * commission_rate_applied"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Observações opcionais sobre as vendas do dia"
    )
    
    # Campo de controle para auditoria
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_registered',
        verbose_name="Lançado por",
        help_text="Usuário que fez o lançamento (pode ser o próprio vendedor ou gerente)"
    )
    
    def save(self, *args, **kwargs):
        """
        Ao salvar, calcula automaticamente a comissão baseada na taxa do vendedor.
        """
        if not self.commission_rate_applied:
            # Captura a taxa atual do vendedor no momento do lançamento
            self.commission_rate_applied = self.seller.commission_rate
        
        # Calcula a comissão
        self.calculated_commission = (self.total_amount * self.commission_rate_applied) / 100
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.seller.get_full_name()} - {self.sale_date} - R$ {self.total_amount}"
    
    class Meta:
        verbose_name = "Venda Diária"
        verbose_name_plural = "Vendas Diárias"
        
        # Um vendedor só pode ter um lançamento por dia
        unique_together = ['seller', 'sale_date']
        
        # Índices para consultas frequentes
        indexes = [
            # Para relatórios por vendedor e período
            models.Index(fields=['seller', 'sale_date']),
            # Para relatórios gerais por período
            models.Index(fields=['sale_date']),
            # Para consultas de vendas ativas
            models.Index(fields=['is_active', 'sale_date']),
        ]