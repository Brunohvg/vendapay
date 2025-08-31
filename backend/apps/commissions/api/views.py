# apps/commissions/views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.models import Account
from ..models import MonthlyCommissionReport
from .serializers import MonthlyCommissionReportSerializer


class MonthlyCommissionReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD e geração de relatórios mensais de comissão.
    """
    queryset = MonthlyCommissionReport.objects.all().order_by('-year', '-month')
    serializer_class = MonthlyCommissionReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['seller', 'year', 'month', 'status']
    ordering_fields = ['year', 'month', 'total_sales_amount', 'total_commission']
    search_fields = ['seller__username', 'seller__first_name', 'seller__last_name']

    def perform_create(self, serializer):
        """
        Cria um relatório a partir dos dados do serializer e calcula os valores
        a partir das vendas existentes.
        """
        report = serializer.save()
        report.calculate_from_sales()
        report.save()

    @action(detail=False, methods=['post'], url_path='generate_all', url_name='generate_all')
    def generate_all_reports(self, request):
        """
        Endpoint: POST /api/v1/monthly-reports/generate_all/
        Gera relatórios para todos os vendedores ativos para o mês e ano especificado.
        Se não houver vendas, o relatório ainda será criado com valores zerados.
        """
        year = request.data.get('year')
        month = request.data.get('month')

        now = timezone.now()
        year = int(year) if year else now.year
        month = int(month) if month else now.month

        # Seleciona todos os vendedores ativos para comissão
        sellers = Account.objects.filter(
            user_type='SELLER',
            commission_active=True,
            is_active=True
        )

        created_reports = []

        for seller in sellers:
            # Cria ou pega o relatório existente
            report, created = MonthlyCommissionReport.objects.get_or_create(
                seller=seller,
                year=year,
                month=month,
                defaults={
                    'total_sales_amount': 0,
                    'sales_days_count': 0,
                    'total_commission': 0,
                    'average_commission_rate': 0,
                }
            )

            # Calcula os valores a partir das vendas, mesmo que seja 0
            report.calculate_from_sales()
            report.save()

            # Serializa o relatório para resposta
            created_reports.append(MonthlyCommissionReportSerializer(report).data)

        return Response({
            "year": year,
            "month": month,
            "reports": created_reports
        })
