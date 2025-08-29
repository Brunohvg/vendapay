from django.urls import path, include

urlpatterns = [
    # Inclui as URLs da API a partir da subpasta 'api', com a versão 'v1'
    path('api/v1/', include('apps.accounts.api.urls')),
    # Outras URLs do app...
]