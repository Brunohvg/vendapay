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
        report = serializer.save()
        report.calculate_from_sales()
        report.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = serializer.validated_data.get('status', instance.status)
        
        update_fields = {}
        
        # Se o status mudou para "APPROVED" ou "PAID" (e ainda não foi aprovado)
        # preenche quem aprovou.
        if (new_status == MonthlyCommissionReport.Status.APPROVED or new_status == MonthlyCommissionReport.Status.PAID) and not instance.approved_by:
             update_fields['approved_by'] = self.request.user

        serializer.save(**update_fields)

    @action(detail=False, methods=['post'], url_path='generate_all', url_name='generate_all')
    def generate_all_reports(self, request):
        year = request.data.get('year')
        month = request.data.get('month')

        now = timezone.now()
        year = int(year) if year else now.year
        month = int(month) if month else now.month

        sellers = Account.objects.filter(
            user_type='SELLER',
            commission_active=True,
            is_active=True
        )

        created_reports = []
        for seller in sellers:
            report, created = MonthlyCommissionReport.objects.get_or_create(
                seller=seller,
                year=year,
                month=month
            )
            report.calculate_from_sales()
            report.save()
            created_reports.append(self.get_serializer(report).data)

        return Response({
            "year": year,
            "month": month,
            "reports": created_reports
        })