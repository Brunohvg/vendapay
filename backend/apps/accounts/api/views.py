# apps/accounts/api/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Account
from .serializers import AccountsSerializer, ChangePasswordSerializer
from apps.core.pagination import StandardResultsSetPagination


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários (Accounts).

    Recursos:
    - Paginação
    - Autenticação obrigatória
    - Permissões diferentes por ação
    - Busca (SearchFilter)
    - Ordenação (OrderingFilter)
    - Filtros avançados via django-filter
    - Endpoints extras: `me/` e `change_password/`

    Exemplos de uso:
    /api/v1/accounts/users/?search=bruno
    /api/v1/accounts/users/?ordering=-date_joined
    /api/v1/accounts/users/?user_type=admin&is_active=true
    /api/v1/accounts/users/me/
    /api/v1/accounts/users/change_password/
    """

    queryset = Account.objects.all()
    serializer_class = AccountsSerializer
    pagination_class = StandardResultsSetPagination

    # 🔒 Permissão padrão (todos devem estar logados)
    permission_classes = [permissions.IsAuthenticated]

    # 🔍 Busca e ordenação
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined']
    ordering = ['username']

    # 🎯 Filtros avançados (via querystring)
    filterset_fields = ['user_type', 'is_active', 'commission_active']

    def get_permissions(self):
        """
        Define permissões por ação:
        - Listar e visualizar: qualquer usuário autenticado
        - Criar, atualizar e excluir: somente admin
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    # 👤 Endpoint: /api/v1/accounts/users/me/
    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        GET  → retorna os dados do usuário logado
        PATCH → atualiza parcialmente os dados do usuário logado
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 🔑 Endpoint: /api/v1/accounts/users/change_password/
    @action(detail=False, methods=['post'], url_path='change_password',
            permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        POST → troca a senha do usuário logado

        Payload:
        {
            "old_password": "atual123",
            "new_password": "nova123"
        }
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {"old_password": "Senha atual incorreta."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if old_password == new_password:
            return Response(
                {"new_password": "A nova senha não pode ser igual à antiga."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Senha alterada com sucesso!"},
                        status=status.HTTP_200_OK)
