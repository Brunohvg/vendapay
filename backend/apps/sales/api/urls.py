from django.db import router
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SaleViewSet


router = DefaultRouter()
router.register(r'sales', SaleViewSet, basename='sale')  # gera /sale

urlpatterns = [
    path('', include(router.urls)),  # -> /api/v1/accounts/users/

]   

