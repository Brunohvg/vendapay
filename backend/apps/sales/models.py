from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel

class DailySales(BaseModel):
    """
    Registro do total de vendas por vendedor em um dia.
    Mantém histórico da taxa aplicada (mesmo que a taxa do vendedor mude depois).
    """

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
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
        null=True,
        blank=True,
        verbose_name="Taxa de Comissão Aplicada (%)",
        help_text="Taxa aplicada no momento do lançamento (mantém histórico)"
    )

    calculated_commission = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Comissão Calculada (R$)",
        help_text="total_amount * (commission_rate_applied / 100)"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Observações opcionais sobre as vendas do dia"
    )

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_registered',
        verbose_name="Lançado por",
        help_text="Usuário que fez o lançamento (vendedor ou gerente/admin)"
    )

    def save(self, *args, **kwargs):
        """
        Ao salvar:
        - Se não houver taxa manual, aplica a taxa do vendedor.
        - Calcula a comissão com base na taxa aplicada.
        """
        # Garante que a taxa de comissão seja preenchida se estiver vazia
        if self.commission_rate_applied is None:
            self.commission_rate_applied = self.seller.commission_rate

        # Calcula a comissão com a lógica correta e refinada
        self.calculated_commission = (self.total_amount * self.commission_rate_applied) / Decimal('100.0')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seller.get_full_name()} - {self.sale_date} - R$ {self.total_amount}"

    class Meta:
        verbose_name = "Venda Diária"
        verbose_name_plural = "Vendas Diárias"
        unique_together = ['seller', 'sale_date']
        indexes = [
            models.Index(fields=['seller', 'sale_date']),
            models.Index(fields=['sale_date']),
            models.Index(fields=['is_active', 'sale_date']),
        ]