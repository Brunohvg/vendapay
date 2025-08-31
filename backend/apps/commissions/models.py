# apps/commissions/models.py
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel
from apps.sales.models import DailySales

class MonthlyCommissionReport(BaseModel):
    """
    Relatório consolidado das comissões de um vendedor em um mês específico.

    FLUXO:
    1. Durante o mês, vendedor lança vendas diárias no DailySales
    2. No final/início do mês, sistema gera automaticamente este relatório
    3. Relatório soma todas as vendas do mês e calcula comissão total
       e média das taxas aplicadas (snapshot)
    4. Gerente/Admin pode aprovar e marcar como pago

    OBSERVAÇÕES DE MELHORIA:
    - average_commission_rate é um snapshot calculado na geração do relatório,
      garantindo consistência histórica mesmo que as taxas do vendedor mudem depois.
    - Validação extra impede duplicidade de relatório para o mesmo vendedor/mês/ano.
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendente de Aprovação'
        APPROVED = 'APPROVED', 'Aprovado para Pagamento' 
        PAID = 'PAID', 'Pago'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='commission_reports',
        verbose_name="Vendedor"
    )
    
    # Período do relatório
    year = models.PositiveIntegerField(
        verbose_name="Ano",
        validators=[MinValueValidator(2025), MaxValueValidator(2100)]
    )
    month = models.PositiveIntegerField(
        verbose_name="Mês", 
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    
    # Dados consolidados
    total_sales_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Total de Vendas no Mês (R$)",
        help_text="Soma de todas as vendas do vendedor neste mês"
    )
    
    sales_days_count = models.PositiveIntegerField(
        verbose_name="Dias com Vendas",
        help_text="Quantidade de dias que o vendedor teve vendas neste mês"
    )
    
    total_commission = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Comissão Total (R$)",
        help_text="Soma de todas as comissões calculadas do mês"
    )
    
    average_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Taxa Média de Comissão (%)",
        help_text="Snapshot da taxa média aplicada no período"
    )
    
    # Controles de status
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status"
    )
    
    # Campos de auditoria/aprovação
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_approved',
        verbose_name="Aprovado por"
    )
    
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Aprovado em")
    
    # Pagamento simples (um único pagamento)
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Pago em")
    payment_notes = models.TextField(blank=True, verbose_name="Observações do Pagamento")

    def __str__(self):
        return f"{self.seller.get_full_name()} - {self.month:02d}/{self.year}"
    
    @property
    def period_display(self):
        """Retorna o período no formato 'Janeiro/2025'."""
        months = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return f"{months[self.month]}/{self.year}"

    def clean(self):
        """
        Validação extra:
        Evita criar mais de um relatório para o mesmo vendedor/mês/ano.
        """
        if MonthlyCommissionReport.objects.exclude(pk=self.pk).filter(
            seller=self.seller, year=self.year, month=self.month
        ).exists():
            raise ValidationError("Já existe um relatório para este vendedor neste mês.")

    def calculate_from_sales(self):
        """
        Gera os valores consolidados do relatório baseado nas vendas do mês.
        Deve ser chamado na hora de criar o relatório.
        """
        sales_qs = DailySales.objects.filter(
            seller=self.seller,
            sale_date__year=self.year,
            sale_date__month=self.month,
            is_active=True
        )

        self.total_sales_amount = sales_qs.aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')

        self.sales_days_count = sales_qs.values('sale_date').distinct().count()

        self.total_commission = sales_qs.aggregate(
            total=models.Sum('calculated_commission')
        )['total'] or Decimal('0.00')

        # Calcula taxa média ponderada
        if self.total_sales_amount > 0:
            weighted_sum = sum(
                (sale.total_amount * (sale.commission_rate_applied or 0))
                for sale in sales_qs
            )
            self.average_commission_rate = Decimal(weighted_sum) / self.total_sales_amount
        else:
            self.average_commission_rate = Decimal('0.00')

    class Meta:
        verbose_name = "Relatório de Comissão Mensal"
        verbose_name_plural = "Relatórios de Comissão Mensais"
        unique_together = ['seller', 'year', 'month']
        indexes = [
            models.Index(fields=['seller', 'year', 'month']),
            models.Index(fields=['status', 'year', 'month']),
            models.Index(fields=['status', 'created_at']),
        ]
