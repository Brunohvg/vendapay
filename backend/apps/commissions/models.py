from decimal import Decimal
from django.db import models
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core.models import BaseModel
from apps.sales.models import DailySales

class MonthlyCommissionReport(BaseModel):
    """
    Relatório consolidado das comissões de um vendedor em um mês específico.
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

    year = models.PositiveIntegerField(
        verbose_name="Ano",
        validators=[MinValueValidator(2024), MaxValueValidator(2100)]
    )
    month = models.PositiveIntegerField(
        verbose_name="Mês",
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    total_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sales_days_count = models.PositiveIntegerField(default=0)
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    average_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reports_approved', verbose_name="Aprovado por"
    )

    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Aprovado em")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Pago em")
    payment_notes = models.TextField(blank=True, verbose_name="Observações do Pagamento")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if not is_new:
            original_status = MonthlyCommissionReport.objects.get(pk=self.pk).status

            if original_status != self.Status.APPROVED and self.status == self.Status.APPROVED:
                if not self.approved_at: self.approved_at = timezone.now()

            if original_status != self.Status.PAID and self.status == self.Status.PAID:
                if not self.approved_at: self.approved_at = timezone.now()
                if not self.paid_at: self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    def calculate_from_sales(self):
        sales_qs = DailySales.objects.filter(
            seller=self.seller, sale_date__year=self.year,
            sale_date__month=self.month, is_active=True
        )
        report_data = sales_qs.aggregate(
            total_sales=Sum('total_amount'),
            total_comm=Sum('calculated_commission'),
            weighted_sum=Sum(ExpressionWrapper(F('total_amount') * F('commission_rate_applied'), output_field=DecimalField())),
            distinct_days=Count('sale_date', distinct=True)
        )
        self.total_sales_amount = report_data['total_sales'] or Decimal('0.00')
        self.sales_days_count = report_data['distinct_days'] or 0
        self.total_commission = report_data['total_comm'] or Decimal('0.00')
        weighted_sum = report_data['weighted_sum'] or Decimal('0.00')
        if self.total_sales_amount > 0:
            self.average_commission_rate = weighted_sum / self.total_sales_amount
        else:
            self.average_commission_rate = Decimal('0.00')

    def __str__(self): return f"{self.seller.get_full_name()} - {self.month:02d}/{self.year}"
    @property
    def period_display(self):
        months = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        return f"{months[self.month]}/{self.year}"
    def clean(self):
        if MonthlyCommissionReport.objects.exclude(pk=self.pk).filter(seller=self.seller, year=self.year, month=self.month).exists():
            raise ValidationError("Já existe um relatório para este vendedor neste mês.")

    class Meta:
        verbose_name = "Relatório de Comissão Mensal"
        verbose_name_plural = "Relatórios de Comissão Mensais"
        unique_together = ['seller', 'year', 'month']