# apps/core/mixins.py

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação padrão reutilizável para todas as APIs.
    Exemplo de uso:
        pagination_class = StandardResultsSetPagination
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
