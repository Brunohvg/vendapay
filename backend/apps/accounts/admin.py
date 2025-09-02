# apps/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

@admin.register(Account)
class AccountAdmin(UserAdmin):
    """
    Configuração do painel de administração para o modelo Account.

    Herda de UserAdmin para manter todos os campos e funcionalidades
    padrão de gerenciamento de usuários (como senhas, grupos e permissões).
    """

    # 1. Copie os fieldsets do UserAdmin original e adicione os seus
    #    Isso garante que a divisão por seções (inclusive a de permissões) seja mantida.
    fieldsets = UserAdmin.fieldsets + (
        ('Dados Adicionais e Comissões', {
            'fields': (
                'user_type', 
                'document', 
                'phone', 
                'commission_rate', 
                'commission_active', 
                'commission_start_date'
            ),
        }),
    )

    # 2. Adicione seus campos customizados ao formulário de criação de usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados Adicionais', {
            'fields': (
                'user_type', 
                'document', 
                'phone', 
                'commission_rate',
            ),
        }),
    )

    # 3. Adicione seus campos à listagem de usuários para fácil visualização
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'user_type', 
        'is_staff'
    ]

    # 4. (Opcional) Adicione seus campos aos filtros da barra lateral
    list_filter = UserAdmin.list_filter + ('user_type', 'commission_active')

    # 5. (Opcional) Adicione seus campos à busca
    search_fields = UserAdmin.search_fields + ('document',)