from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='main_dashboard'),
    path('vendedor/', views.VendedorDashboardView.as_view(), name='vendedor_dashboard'),
]
