from rest_framework import viewsets
from apps.core.pagination import StandardResultsSetPagination
from .serializers import SalesSerializer
from ..models import DailySales

class SaleModelViewSet(viewsets.ModelViewSet):
    queryset = DailySales.objects.all().select_related().prefetch_related()
    serializer_class = SalesSerializer
    pagination_class = StandardResultsSetPagination
