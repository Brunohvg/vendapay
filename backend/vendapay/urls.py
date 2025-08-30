from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas Web do app accounts
    path('accounts/', include('apps.accounts.urls')),

    # Rotas API global do app accounts
    path('api/v1/accounts/', include('apps.accounts.api.urls')),

    # Rotas Api global do app sales
    path('api/v1/sales/', include('apps.sales.api.urls'))
]
