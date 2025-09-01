from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas Web do app accounts
    #path('accounts/', include('apps.accounts.urls')),
    path('contas/', include('apps.accounts.urls')),

    # Rotas API global do app accounts
    path('api/v1/', include('apps.accounts.api.urls')),

    # Rotas Api global do app sales
    path('api/v1/', include('apps.sales.api.urls')),
        
    path('api/v1/', include('apps.commissions.api.urls')),
    path('', include('apps.dashboard.urls')), # Dashboard é a página inicial

]
