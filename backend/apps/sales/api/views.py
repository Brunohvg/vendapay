from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.pagination import StandardResultsSetPagination
from .serializers import SalesSerializer
from ..models import DailySales

class SaleViewSet(viewsets.ModelViewSet):
    queryset = DailySales.objects.all().select_related("seller", "registered_by")
    serializer_class = SalesSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['seller', 'sale_date', 'is_active']  # 🔹 campos filtráveis
    ordering_fields = ['sale_date', 'total_amount', 'calculated_commission']
    search_fields = ['seller__username', 'seller__first_name', 'seller__last_name']

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(registered_by=self.request.user)
